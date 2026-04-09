// Top-down Action Shooter Game Logic
// Features: Physics, Collision, NPC AI, and State Management

class GameEngine {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        
        this.player = {
            x: this.width / 2,
            y: this.height / 2,
            size: 20,
            color: '#00ff00',
            speed: 5,
            hp: 100,
            score: 0
        };
        
        this.projectiles = [];
        this.enemies = [];
        this.keys = {};
        
        this.lastEnemySpawn = 0;
        this.enemySpawnRate = 2000; // ms
        
        window.addEventListener('keydown', (e) => this.keys[e.key] = true);
        window.addEventListener('keyup', (e) => this.keys[e.key] = false);
        window.addEventListener('mousedown', (e) => this.shoot(e));
        
        this.isGameOver = false;
    }

    shoot(e) {
        if (this.isGameOver) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const angle = Math.atan2(mouseY - this.player.y, mouseX - this.player.x);
        
        this.projectiles.push({
            x: this.player.x,
            y: this.player.y,
            vx: Math.cos(angle) * 10,
            vy: Math.sin(angle) * 10,
            size: 5,
            color: '#ffff00'
        });
    }

    spawnEnemy() {
        const side = Math.floor(Math.random() * 4);
        let x, y;
        
        if (side === 0) { x = Math.random() * this.width; y = -20; }
        else if (side === 1) { x = this.width + 20; y = Math.random() * this.height; }
        else if (side === 2) { x = Math.random() * this.width; y = this.height + 20; }
        else { x = -20; y = Math.random() * this.height; }
        
        this.enemies.push({
            x, y,
            size: 25,
            color: '#ff0000',
            speed: 2 + Math.random() * 2,
            hp: 20
        });
    }

    update() {
        if (this.isGameOver) return;

        // Player movement
        if (this.keys['w'] || this.keys['ArrowUp']) this.player.y -= this.player.speed;
        if (this.keys['s'] || this.keys['ArrowDown']) this.player.y += this.player.speed;
        if (this.keys['a'] || this.keys['ArrowLeft']) this.player.x -= this.player.speed;
        if (this.keys['d'] || this.keys['ArrowRight']) this.player.x += this.player.speed;

        // Keep player in bounds
        this.player.x = Math.max(this.player.size, Math.min(this.width - this.player.size, this.player.x));
        this.player.y = Math.max(this.player.size, Math.min(this.height - this.player.size, this.player.y));

        // Update projectiles
        this.projectiles.forEach((p, i) => {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0 || p.x > this.width || p.y < 0 || p.y > this.height) {
                this.projectiles.splice(i, 1);
            }
        });

        // Update enemies
        const now = Date.now();
        if (now - this.lastEnemySpawn > this.enemySpawnRate) {
            this.spawnEnemy();
            this.lastEnemySpawn = now;
        }

        this.enemies.forEach((enemy, i) => {
            const angle = Math.atan2(this.player.y - enemy.y, this.player.x - enemy.x);
            enemy.x += Math.cos(angle) * enemy.speed;
            enemy.y += Math.sin(angle) * enemy.speed;

            // Collision with player
            const dist = Math.hypot(this.player.x - enemy.x, this.player.y - enemy.y);
            if (dist < this.player.size + enemy.size) {
                this.player.hp -= 1;
                if (this.player.hp <= 0) this.isGameOver = true;
            }

            // Collision with projectiles
            this.projectiles.forEach((p, pi) => {
                const pDist = Math.hypot(p.x - enemy.x, p.y - enemy.y);
                if (pDist < p.size + enemy.size) {
                    enemy.hp -= 10;
                    this.projectiles.splice(pi, 1);
                    if (enemy.hp <= 0) {
                        this.enemies.splice(i, 1);
                        this.player.score += 100;
                    }
                }
            });
        });
    }

    draw() {
        this.ctx.fillStyle = '#111';
        this.ctx.fillRect(0, 0, this.width, this.height);

        if (this.isGameOver) {
            this.ctx.fillStyle = '#fff';
            this.ctx.font = '40px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('GAME OVER', this.width / 2, this.height / 2);
            this.ctx.font = '20px Arial';
            this.ctx.fillText(`Final Score: ${this.player.score}`, this.width / 2, this.height / 2 + 40);
            return;
        }

        // Draw player
        this.ctx.fillStyle = this.player.color;
        this.ctx.beginPath();
        this.ctx.arc(this.player.x, this.player.y, this.player.size, 0, Math.PI * 2);
        this.ctx.fill();

        // Draw projectiles
        this.projectiles.forEach(p => {
            this.ctx.fillStyle = p.color;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fill();
        });

        // Draw enemies
        this.enemies.forEach(enemy => {
            this.ctx.fillStyle = enemy.color;
            this.ctx.beginPath();
            this.ctx.arc(enemy.x, enemy.y, enemy.size, 0, Math.PI * 2);
            this.ctx.fill();
        });

        // UI
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '20px Arial';
        this.ctx.fillText(`Score: ${this.player.score}`, 10, 30);
        this.ctx.fillText(`HP: ${this.player.hp}`, 10, 60);
    }

    getState() {
        return {
            player: this.player,
            enemies: this.enemies,
            score: this.player.score
        };
    }

    setState(state) {
        if (!state) return;
        this.player = { ...this.player, ...state.player };
        this.enemies = state.enemies || [];
        this.player.score = state.score || 0;
    }

    loop() {
        this.update();
        this.draw();
        requestAnimationFrame(() => this.loop());
    }
}
