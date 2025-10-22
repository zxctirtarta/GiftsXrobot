const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// гровые переменные
let gameActive = false;
let crashPoint = 0;
let currentMultiplier = 1.00;
let interval;
const BACKEND_URL = 'https://giftsxrobot-xxx.vercel.app'; // бнови после депло€!

// риветствие
const userName = tg.initDataUnsafe?.user?.first_name || 'грок';
document.getElementById('welcome-text').textContent = ривет, ! ??;

// TON Connect
const tonConnectUI = new TON_CONNECT_UI.TonConnectUI({
    manifestUrl: 'tonconnect-manifest.json',
    buttonRootId: 'connect-wallet'
});

tonConnectUI.onStatusChange(wallet => {
    if (wallet) {
        document.getElementById('connect-section').style.display = 'none';
        document.getElementById('game-section').style.display = 'block';
        updateBalance();
    }
});

// бновление баланса (демо)
async function updateBalance() {
    document.getElementById('balance').textContent = '0.50 TON';
}

// ??  џ
document.getElementById('bet-btn').addEventListener('click', async () => {
    if (gameActive) return;
    
    gameActive = true;
    const betBtn = document.getElementById('bet-btn');
    const cashoutBtn = document.getElementById('cashout-btn');
    const status = document.getElementById('status');
    
    betBtn.style.display = 'none';
    cashoutBtn.style.display = 'inline-block';
    status.textContent = '?? апуск...';
    
    // олучаем точку краша от бэкенда
    try {
        const response = await fetch(${BACKEND_URL}/api/generate_crash);
        const data = await response.json();
        crashPoint = data.crash_point;
    } catch(e) {
        // Fallback дл€ теста
        crashPoint = Math.random() < 0.5 ? 1.5 : Math.random() * 10 + 1;
    }
    
    currentMultiplier = 1.00;
    updateMultiplier();
    
    // нимаци€ роста множител€
    interval = setInterval(() => {
        if (currentMultiplier >= crashPoint) {
            // ?? Ў!
            gameActive = false;
            clearInterval(interval);
            
            const multiplierEl = document.getElementById('multiplier');
            multiplierEl.textContent = '?? CRASH!';
            multiplierEl.className = 'crash-animation';
            status.textContent = раш на x;
            
            betBtn.style.display = 'inline-block';
            cashoutBtn.style.display = 'none';
            
            setTimeout(() => {
                multiplierEl.className = 'multiplier-green';
                multiplierEl.textContent = '1.00x';
                status.textContent = '?? отов к игре';
            }, 2000);
        } else {
            currentMultiplier += 0.05;
            updateMultiplier();
        }
    }, 80); // ыстрее анимаци€!
});

// бновление множител€ + цвета
function updateMultiplier() {
    const elem = document.getElementById('multiplier');
    elem.textContent = ${currentMultiplier.toFixed(2)}x;
    
    if (currentMultiplier < 2) {
        elem.className = 'multiplier-green';
    } else if (currentMultiplier < 5) {
        elem.className = 'multiplier-yellow';
    } else {
        elem.className = 'multiplier-red';
    }
}

// ??  џ
document.getElementById('cashout-btn').addEventListener('click', () => {
    if (!gameActive) return;
    
    gameActive = false;
    clearInterval(interval);
    
    const status = document.getElementById('status');
    status.textContent = ? ывод на x!;
    
    document.getElementById('bet-btn').style.display = 'inline-block';
    document.getElementById('cashout-btn').style.display = 'none';
    
    setTimeout(() => {
        document.getElementById('multiplier').className = 'multiplier-green';
        document.getElementById('multiplier').textContent = '1.00x';
        status.textContent = '?? отов к игре';
    }, 2000);
});
