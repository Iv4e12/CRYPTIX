
const $ = id => document.getElementById(id);

const demoMessage =
"This is a demo. Install the program to access all features ;(";

// Navigation
function openPage(page) {
    document.querySelectorAll(".page").forEach(section => {
        section.classList.toggle("active", section.id === page);
    });

    document.querySelectorAll(".nav-item").forEach(button => {
        button.classList.toggle("active", button.dataset.page === page);
    });

    const titles = {
        dashboard: "Dashboard",
        encryption: "Encryption",
        hashing: "Hashing",
        password: "Password Lab",
        cipher: "Cipher Lab",
        vault: "Key Vault",
        history: "History"
    };

    $("page-title").textContent = titles[page] || "Dashboard";
}

document.querySelectorAll("[data-page]").forEach(button => {
    button.addEventListener("click", () => openPage(button.dataset.page));
});

document.querySelectorAll("[data-open]").forEach(button => {
    button.addEventListener("click", () => openPage(button.dataset.open));
});

// Clipboard
async function copyText(value, statusElement) {
    if (!value) {
        statusElement.textContent = "Nothing to copy.";
        return;
    }

    try {
        await navigator.clipboard.writeText(value);
        statusElement.textContent = "Copied to clipboard.";
    } catch {
        statusElement.textContent = "Clipboard access unavailable.";
    }
}

// AES-256-GCM encryption
async function deriveKey(password, salt) {
    const encodedPassword = new TextEncoder().encode(password);

    const material = await crypto.subtle.importKey(
        "raw",
        encodedPassword,
        "PBKDF2",
        false,
        ["deriveKey"]
    );

    return crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt,
            iterations: 250000,
            hash: "SHA-256"
        },
        material,
        {
            name: "AES-GCM",
            length: 256
        },
        false,
        ["encrypt", "decrypt"]
    );
}

$("encrypt-btn").addEventListener("click", async () => {
    const password = $("aes-password").value;
    const input = $("aes-input").value;

    if (!password || !input) {
        $("aes-status").textContent = "Enter a password and some text.";
        return;
    }

    try {
        const salt = crypto.getRandomValues(new Uint8Array(16));
        const iv = crypto.getRandomValues(new Uint8Array(12));
        const key = await deriveKey(password, salt);

        const encrypted = await crypto.subtle.encrypt(
            { name: "AES-GCM", iv },
            key,
            new TextEncoder().encode(input)
        );

        const combined = new Uint8Array(
            salt.length + iv.length + encrypted.byteLength
        );

        combined.set(salt, 0);
        combined.set(iv, salt.length);
        combined.set(new Uint8Array(encrypted), salt.length + iv.length);

        let binary = "";
        combined.forEach(byte => binary += String.fromCharCode(byte));

        $("aes-output").value = btoa(binary);
        $("aes-status").textContent = "Encryption completed successfully.";
    } catch {
        $("aes-status").textContent = "Encryption failed.";
    }
});

$("decrypt-btn").addEventListener("click", async () => {
    const password = $("aes-password").value;
    const input = $("aes-input").value.trim();

    if (!password || !input) {
        $("aes-status").textContent = "Enter a password and encrypted data.";
        return;
    }

    try {
        const binary = atob(input);
        const combined = Uint8Array.from(
            binary,
            character => character.charCodeAt(0)
        );

        if (combined.length < 45) {
            throw new Error("Invalid data");
        }

        const salt = combined.slice(0, 16);
        const iv = combined.slice(16, 28);
        const encrypted = combined.slice(28);

        const key = await deriveKey(password, salt);

        const decrypted = await crypto.subtle.decrypt(
            { name: "AES-GCM", iv },
            key,
            encrypted
        );

        $("aes-output").value = new TextDecoder().decode(decrypted);
        $("aes-status").textContent = "Decryption completed successfully.";
    } catch {
        $("aes-output").value = "";
        $("aes-status").textContent = "Decryption failed. Check your password and data.";
    }
});

$("copy-aes").addEventListener("click", () => {
    copyText($("aes-output").value, $("aes-status"));
});

// SHA-256 hashing
$("hash-btn").addEventListener("click", async () => {
    const input = $("hash-input").value;

    if (!input) {
        $("hash-status").textContent = "Enter some text first.";
        return;
    }

    try {
        const data = new TextEncoder().encode(input);
        const digest = await crypto.subtle.digest("SHA-256", data);

        $("hash-output").value = Array.from(new Uint8Array(digest))
        .map(byte => byte.toString(16).padStart(2, "0"))
        .join("");

        $("hash-status").textContent = "Hash generated successfully.";
    } catch {
        $("hash-status").textContent = "Hashing failed.";
    }
});

$("copy-hash").addEventListener("click", () => {
    copyText($("hash-output").value, $("hash-status"));
});

// Password generator
$("password-length").addEventListener("input", event => {
    $("length-value").textContent = event.target.value;
});

function secureRandomIndex(max) {
    const limit = Math.floor(4294967296 / max) * max;
    const array = new Uint32Array(1);

    do {
        crypto.getRandomValues(array);
    } while (array[0] >= limit);

    return array[0] % max;
}

$("generate-password").addEventListener("click", () => {
    const groups = [];

    if ($("upper").checked) groups.push("ABCDEFGHIJKLMNOPQRSTUVWXYZ");
    if ($("lower").checked) groups.push("abcdefghijklmnopqrstuvwxyz");
    if ($("numbers").checked) groups.push("0123456789");
    if ($("symbols").checked) groups.push("!@#$%^&*()-_=+[]{};:,.?");

    if (!groups.length) {
        $("password-status").textContent = "Select at least one character set.";
        return;
    }

    const pool = groups.join("");
    const length = Number($("password-length").value);

    const result = groups.map(group =>
    group[secureRandomIndex(group.length)]
    );

    while (result.length < length) {
        result.push(pool[secureRandomIndex(pool.length)]);
    }

    for (let i = result.length - 1; i > 0; i--) {
        const j = secureRandomIndex(i + 1);
        [result[i], result[j]] = [result[j], result[i]];
    }

    const password = result.join("");
    $("password-output").value = password;

    const entropy = length * Math.log2(pool.length);

    let strength = "Weak";
    if (entropy >= 80) strength = "Very Strong";
    else if (entropy >= 60) strength = "Strong";
    else if (entropy >= 40) strength = "Moderate";

    $("strength").textContent = `Strength: ${strength}`;
    $("entropy").textContent = `Estimated entropy: ${entropy.toFixed(1)} bits`;
    $("password-status").textContent = "Password generated successfully.";
});

$("copy-password").addEventListener("click", () => {
    copyText($("password-output").value, $("password-status"));
});

// Classical ciphers
$("cipher-type").addEventListener("change", () => {
    $("shift-container").style.display =
    $("cipher-type").value === "caesar" ? "block" : "none";
});

function caesar(text, shift) {
    return [...text].map(char => {
        if (!/[a-z]/i.test(char) || !/[a-z]/i.test(char)) return char;

        const base = char === char.toUpperCase() ? 65 : 97;

        return String.fromCharCode(
            ((char.charCodeAt(0) - base + shift + 26) % 26) + base
        );
    }).join("");
}

function atbash(text) {
    return [...text].map(char => {
        if (!/[a-z]/i.test(char)) return char;

        const base = char === char.toUpperCase() ? 65 : 97;

        return String.fromCharCode(
            base + 25 - (char.charCodeAt(0) - base)
        );
    }).join("");
}

function processCipher(encrypting) {
    const text = $("cipher-input").value;

    if (!text) {
        $("cipher-status").textContent = "Enter some text first.";
        return;
    }

    const type = $("cipher-type").value;
    const shift = Number($("shift-value").value);

    let result;

    if (type === "caesar") {
        if (!Number.isInteger(shift) || shift < 1 || shift > 25) {
            $("cipher-status").textContent = "Shift must be between 1 and 25.";
            return;
        }

        result = caesar(text, encrypting ? shift : -shift);
    } else {
        result = atbash(text);
    }

    $("cipher-output").value = result;
    $("cipher-status").textContent =
    `Text ${encrypting ? "encrypted" : "decrypted"} successfully.`;
}

$("cipher-encrypt").addEventListener("click", () => processCipher(true));
$("cipher-decrypt").addEventListener("click", () => processCipher(false));

$("copy-cipher").addEventListener("click", () => {
    copyText($("cipher-output").value, $("cipher-status"));
});
