import sys
import socket
import threading
import datetime
import os

# --- 設定 ---
ROLE = "HOST"  # ホストなら "HOST"、ゲストなら "GUEST"
SERVER_IP = "192.168.x.xx"
PORT = 12345
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"log_bridge_{ROLE.lower()}.log")

# グローバル変数
last_genmove_id = None
last_play_id = None

def log_message(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        ts = datetime.datetime.now().strftime("%H:%M:%S.%f")
        f.write(f"[{ts}] {msg}\n")
        f.flush()

def network_to_sabaki(sock):
    """ネットワークから届いたデータを Sabaki に変換して流す"""
    global last_genmove_id, last_play_id
    try:
        f_sock = sock.makefile('r', encoding='utf-8')
        while True:
            line = f_sock.readline()
            if not line: break
            
            raw = line.strip()
            if not raw: continue
            
            # --- 重要: ネットワークからの play 命令を genmove の応答に変換 ---
            if "play" in raw:
                move = raw.split()[-1]
                
                # もし Sabaki が genmove を待っていたなら、応答 (=ID 座標) に変換
                if last_genmove_id is not None:
                    response = f"={last_genmove_id} {move}\n\n"
                    sys.stdout.write(response)
                    sys.stdout.flush()
                    log_message(f"CONVERTED PLAY TO RESP: {response.strip()}")
                    last_genmove_id = None
                else:
                    # そうでなければ play 命令として流して、自動応答を返す
                    sys.stdout.write(line)
                    sys.stdout.flush()
                    log_message(f"NET -> SABAKI (raw play): {raw}")
                    sys.stdout.write("= \n\n")
                    sys.stdout.flush()
                    log_message("SENT AUTO-RESPONSE TO NET PLAY")

            # 2. 応答(=)の処理 (genmove の結果)
            elif raw.startswith("=") and last_genmove_id is not None:
                response = f"={last_genmove_id} {raw[1:].strip()}\n\n"
                sys.stdout.write(response)
                sys.stdout.flush()
                log_message(f"CONVERTED GENMOVE RESP: {response.strip()}")
                last_genmove_id = None
            
            # 3. それ以外(命令など)
            else:
                sys.stdout.write(line)
                sys.stdout.flush()
                log_message(f"NET -> SABAKI (raw): {raw}")

    except Exception as e:
        log_message(f"Network error: {e}")

def handle_local_commands(line):
    global last_genmove_id, last_play_id
    raw = line.strip()
    if not raw: return None, False
    
    parts = raw.split()
    # IDがある場合は parts[0] が数字、parts[1] がコマンド名
    if parts[0].isdigit():
        res_id = parts[0]
        cmd = parts[1].lower() if len(parts) > 1 else ""
    else:
        res_id = ""
        cmd = parts[0].lower()

    # 即答系コマンドに lz-analyze と time_settings を追加
    if cmd in ['protocol_version', 'name', 'version', 'list_commands', 'boardsize', 'clear_board', 'komi', 'lz-analyze', 'time_settings']:
        res_body = ""
        if cmd == 'protocol_version': res_body = "2"
        elif cmd == 'name': res_body = f"NetBridge_{ROLE}"
        elif cmd == 'version': res_body = "2.3"
        elif cmd == 'list_commands': res_body = "protocol_version\nname\nversion\nlist_commands\nboardsize\nclear_board\nkomi\nplay\ngenmove\nquit\nlz-analyze\ntime_settings"
        # lz-analyze や time_settings には空の成功応答を返す
        return f"={res_id} {res_body}\n\n", True

    if cmd == 'genmove':
        last_genmove_id = res_id
        # genmove b -> genmove B に正規化して送る
        color = parts[-1].upper()
        normalized_raw = f"{res_id} genmove {color}".strip()
        return normalized_raw, False
    
    if cmd == 'play':
        res_id_str = res_id if res_id else ""
        response_to_sabaki = f"={res_id_str}\n\n"
        sys.stdout.write(response_to_sabaki)
        sys.stdout.flush()
        log_message(f"LOCAL RESP (play ok): {response_to_sabaki.strip()}")
        
        # play b q16 -> play B Q16 に正規化
        color = parts[-2].upper()
        move = parts[-1].upper()
        normalized_raw = f"{res_id} play {color} {move}".strip()
        return normalized_raw, False

    return raw, False

def main():
    log_message(f"Starting Bridge v2.3 as {ROLE}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if ROLE == "HOST":
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", PORT))
        sock.listen(1)
        conn, addr = sock.accept()
        log_message(f"Connected from {addr}")
    else:
        try:
            sock.connect((SERVER_IP, PORT))
            conn = sock
        except Exception as e:
            log_message(f"Connection failed: {e}")
            return

    threading.Thread(target=network_to_sabaki, args=(conn,), daemon=True).start()

    while True:
        line = sys.stdin.readline()
        if not line: break
        
        response, is_immediate = handle_local_commands(line)
        
        if is_immediate:
            sys.stdout.write(response)
            sys.stdout.flush()
            log_message(f"LOCAL IMMEDIATE RESP: {response.strip()}")
            if any(x in line for x in ['boardsize', 'clear_board', 'komi']):
                conn.sendall(line.encode())
        else:
            log_message(f"SABAKI -> NET: {line.strip()}")
            conn.sendall(line.encode())

if __name__ == "__main__":
    main()
