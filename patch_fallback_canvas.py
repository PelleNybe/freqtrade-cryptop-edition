with open("freqtrade/rpc/api_server/ui/fallback_file.html") as f:
    content = f.read()

styles = """
    #particle-canvas {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: -1;
      pointer-events: all;
    }
"""
content = content.replace("</style>", styles + "</style>")

# Add the canvas
content = content.replace("<body>", '<body>\n  <canvas id="particle-canvas"></canvas>')

# Add JS logic
js = """
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');
    let width, height, particles;

    function initCanvas() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        particles = [];
        for (let i = 0; i < 80; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 1.5,
                vy: (Math.random() - 0.5) * 1.5,
                radius: Math.random() * 2 + 1
            });
        }
    }

    let mouse = { x: null, y: null };
    window.addEventListener('mousemove', e => {
        mouse.x = e.x;
        mouse.y = e.y;
    });

    window.addEventListener('resize', initCanvas);

    function drawParticles() {
        ctx.clearRect(0, 0, width, height);

        ctx.fillStyle = 'rgba(0, 240, 255, 0.5)';
        ctx.strokeStyle = 'rgba(255, 42, 133, 0.2)';

        for (let i = 0; i < particles.length; i++) {
            let p = particles[i];

            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > width) p.vx = -p.vx;
            if (p.y < 0 || p.y > height) p.vy = -p.vy;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fill();

            for (let j = i + 1; j < particles.length; j++) {
                let p2 = particles[j];
                let dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }

            if (mouse.x && mouse.y) {
                let mouseDist = Math.hypot(p.x - mouse.x, p.y - mouse.y);
                if (mouseDist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.strokeStyle = `rgba(0, 240, 255, ${1 - mouseDist/150})`;
                    ctx.stroke();
                    ctx.strokeStyle = 'rgba(255, 42, 133, 0.2)';
                }
            }
        }
        requestAnimationFrame(drawParticles);
    }

    initCanvas();
    drawParticles();
"""
content = content.replace("</script>", js + "\n</script>")


with open("freqtrade/rpc/api_server/ui/fallback_file.html", "w") as f:
    f.write(content)
