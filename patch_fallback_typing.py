with open("freqtrade/rpc/api_server/ui/fallback_file.html") as f:
    content = f.read()

# Add JS logic
js = """
    function typeWriter(element, text, speed, callback) {
      let i = 0;
      element.innerHTML = '';
      function type() {
        if (i < text.length) {
          element.innerHTML += text.charAt(i);
          i++;
          setTimeout(type, speed);
        } else if (callback) {
          callback();
        }
      }
      type();
    }

    document.addEventListener("DOMContentLoaded", () => {
      const cmd1 = document.getElementById('cmd-native');
      const cmd2 = document.getElementById('cmd-docker');
      const text1 = cmd1.innerText;
      const text2 = cmd2.innerText;

      cmd1.innerText = '';
      cmd2.innerText = '';

      setTimeout(() => {
          typeWriter(cmd1, text1, 30, () => {
              typeWriter(cmd2, text2, 30);
          });
      }, 500);
    });
"""
content = content.replace("</script>", js + "\n</script>")


with open("freqtrade/rpc/api_server/ui/fallback_file.html", "w") as f:
    f.write(content)
