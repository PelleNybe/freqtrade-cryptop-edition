with open("freqtrade/rpc/api_server/api_v1.py") as f:
    content = f.read()

# I removed ALL `except Exception as e:`, I need to restore them where `e` is used.
# But looking at line 130: `raise HTTPException(status_code=502, detail=str(e))`
# It means it was `except Exception as e:` there.

content = content.replace(
    """    except Exception:
        raise HTTPException(status_code=502, detail=str(e))""",
    """    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))""",
)

with open("freqtrade/rpc/api_server/api_v1.py", "w") as f:
    f.write(content)
