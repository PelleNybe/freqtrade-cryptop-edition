with open("freqtrade/rpc/api_server/ui/fallback_file.html") as f:
    content = f.read()

styles = """
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
      width: 10px;
    }
    ::-webkit-scrollbar-track {
      background: var(--bg-base);
    }
    ::-webkit-scrollbar-thumb {
      background: var(--bg-glass);
      border-radius: 5px;
      border: 1px solid var(--accent-1);
    }
    ::-webkit-scrollbar-thumb:hover {
      background: var(--accent-1);
      box-shadow: 0 0 10px var(--accent-1);
    }

    /* Enhanced Glows */
    .card.glass:hover {
        box-shadow: 0 8px 32px 0 rgba(255, 42, 133, 0.2);
        border: 1px solid rgba(255, 42, 133, 0.4);
    }
    .card.glass.alt:hover {
        box-shadow: 0 8px 32px 0 rgba(0, 240, 255, 0.2);
        border: 1px solid rgba(0, 240, 255, 0.4);
    }
    .btn-primary:hover {
        box-shadow: 0 0 25px var(--accent-2);
        transform: translateY(-2px);
    }
"""
content = content.replace("</style>", styles + "</style>")

with open("freqtrade/rpc/api_server/ui/fallback_file.html", "w") as f:
    f.write(content)
