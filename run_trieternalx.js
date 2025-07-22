const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const pythonExec = process.platform === 'win32' ? 'python' : 'python3';

const pythonScript = path.join(__dirname, 'TrieternalX.py');

if (!fs.existsSync(pythonScript)) {
    console.error('[❌] Error: File "TrieternalX.py" tidak ditemukan.');
    process.exit(1);
}

function checkPython() {
    return new Promise((resolve, reject) => {
        const check = spawn(pythonExec, ['--version']);
        check.stdout.on('data', (data) => {
            console.log(`[✔] Python version: ${data.toString().trim()}`);
        });
        check.on('error', () => reject(new Error('Python tidak ditemukan dalam PATH sistem.')));
        check.on('close', (code) => {
            if (code === 0) resolve(true);
            else reject(new Error('Gagal mengecek versi Python.'));
        });
    });
}

function checkDependencies() {
    return new Promise((resolve, reject) => {
        const required = [
            'tkinter', 'requests', 'cv2', 'mediapipe',
            'screen_brightness_control', 'speedtest',
            'inference', 'PIL', 'keyboard'
        ];
        const importTest = `try:\n  ` + required.map(r => `import ${r}`).join('\n  ') + `\n  print("ok")\nexcept Exception as e:\n  print("missing:", e)\n  exit(1)`;
        const depCheck = spawn(pythonExec, ['-c', importTest]);

        depCheck.stdout.on('data', (data) => {
            if (!data.toString().includes('ok')) {
                console.warn(`[⚠️] Dependency info: ${data.toString().trim()}`);
            }
        });

        depCheck.on('exit', (code) => {
            if (code === 0) resolve(true);
            else reject(new Error('Beberapa dependency Python tidak terpasang.'));
        });
    });
}

async function runPythonScript() {
    try {
        await checkPython();
        await checkDependencies();
        console.log('[🚀] Menjalankan TrieternalX.py ...');

        const python = spawn(pythonExec, [pythonScript], {
            stdio: ['pipe', 'pipe', 'pipe'],
            env: { ...process.env, PYTHONUNBUFFERED: '1' }
        });

        python.stdout.on('data', (data) => {
            const out = data.toString().trim();
            if (out) console.log(`[📤 Python]: ${out}`);
        });

        python.stderr.on('data', (data) => {
            const err = data.toString().trim();
            if (err) console.error(`[🔥 Python Error]: ${err}`);
        });

        python.on('close', (code) => {
            console.log(`[📦] Proses Python selesai dengan kode: ${code}`);
            if (code !== 0) {
                console.error('[❗] Python keluar secara tidak normal.');
            }
        });

        python.on('error', (err) => {
            console.error(`[💥] Gagal menjalankan Python: ${err.message}`);
        });

        process.on('SIGINT', () => {
            console.log('\n[🛑] Mengakhiri proses Python...');
            python.kill('SIGTERM');
            process.exit(0);
        });

    } catch (err) {
        console.error(`[❌] Error: ${err.message}`);
        process.exit(1);
    }
}

// Jalankan
runPythonScript();