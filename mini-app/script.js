const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

let gameActive = false;
let crashPoint = 0;
let currentMultiplier = 1.00;
let interval;
const BACKEND_URL = 'https://giftsxrobot-backend.vercel.app';

document.querySelector('.header h1').insertAdjacentHTML('afterend', 
    <p style="opacity: 0.8;">ривет, ! 👋</p>
);

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

async function updateBalance() {
    document.getElementById('balance').textContent = '0.50 TON';
}

document.getElementById('bet-btn').addEventListener('click', async () => {
    if (gameActive) return;
    
    gameActive = true;
    document.getElementById('bet-btn').style.display = 'none';
    document.getElementById('cashout-btn').style.display = 'inline-block';
    document.getElementById('status').textContent = '🚀 апуск...';
    
    const response = await fetch(${BACKEND_URL}/api/generate_crash);
    const data = await response.json();
    crashPoint = data.crash_point;
    
    currentMultiplier = 1.00;
    updateMultiplier();
    
    interval = setInterval(() => {
        if (currentMultiplier >= crashPoint) {
            gameActive = false;
            clearInterval(interval);
            document.getElementById('multiplier').textContent = '💥 CRASH!';
            document.getElementById('multiplier').classList.add('crash-animation');
            document.getElementById('status').textContent = раш на x;
            document.getElementById('bet-btn').style.display = 'inline-block';
            document.getElementById('cashout-btn').style.display = 'none';
            setTimeout(() => {
                document.getElementById('multiplier').classList.remove('crash-animation');
            }, 500);
        } else {
            currentMultiplier += 0.05;
            updateMultiplier();
        }
    }, 100);
});

function updateMultiplier() {
    const elem = document.getElementById('multiplier');
    elem.textContent = ${currentMultiplier.toFixed(2)}x;
    
    if (currentMultiplier < 2) elem.style.color = '#00ff80';
    else if (currentMultiplier < 5) elem.style.color = '#ffd700';
    else elem.style.color = '#ff6b6b';
}

document.getElementById('cashout-btn').addEventListener('click', () => {
    if (!gameActive) return;
    
    gameActive = false;
    clearInterval(interval);
    document.getElementById('status').textContent = ✅ ывод на x!;
    document.getElementById('bet-btn').style.display = 'inline-block';
    document.getElementById('cashout-btn').style.display = 'none';
});
