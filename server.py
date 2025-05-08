import asyncio
import logging
import argparse
import os
from urllib.parse import parse_qs

APP_LOGGER = logging.getLogger(name="HTTP AsyncIO Concurrent Server")
APP_LOGGER.setLevel(logging.DEBUG)
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(logging.Formatter(fmt="[%(levelname)s] %(name)s : %(asctime)s > %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
APP_LOGGER.addHandler(logging_handler)

ma_html_files = "templates"

def parse_args():
    parser = argparse.ArgumentParser(description="HTTP AsyncIO Concurrent Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host Address to bind to")
    parser.add_argument("--port", type=int, required=True, help="Port to bind to")
    return parser.parse_args()

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    APP_LOGGER.debug(f"Connected to {addr}")

    try:
        data = await reader.read(1024)
        if not data:
            APP_LOGGER.debug(f"Connection closed by {addr}")
            return

        request = data.decode()
        request_line = request.split('\r\n')[0]
        parts = request_line.split()
        if len(parts) < 3:
            APP_LOGGER.error(f"invalid HTTP request from {addr}")
            writer.close()
            await writer.wait_closed()
            return

        method, path, _ = parts

        APP_LOGGER.info(f"Received {method} request for {path}")

        if method == "GET":
            if path == "/":
                response_body = await read_templates("index.html")
                if response_body is None:
                    await send_404(writer)
                    return
                await send_response(writer, response_body, content_type="text/html")
            elif path == "/register":
                response_body = await read_templates("register.html")
                if response_body is None:
                    await send_404(writer)
                    return
                await send_response(writer, response_body, content_type="text/html")
            else:
                await send_404(writer)

        elif method == "POST":
            if path == "/submit":
                headers_end = request.find('\r\n\r\n')
                body = request[headers_end+4:]
                form_data = parse_qs(body)
                username = form_data.get('username', [''])[0]
                email = form_data.get('email', [''])[0]

                if username and email:
                    with open("db.txt", "a") as file:
                        file.write(f"{username} {email}\n")

                    response_body = f"Thank you {username}, we have received your email {email}."
                    await send_response(writer, response_body, content_type="text/plain")
                else:
                    await send_400(writer)
            else:
                await send_404(writer)

        else:
            await send_400(writer)

    except Exception as e:
        APP_LOGGER.error(f"Error handling client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def read_templates(filename):
    try:
        path = os.path.join(ma_html_files, filename)
        def read_file():
            with open(path, 'r') as f:
                return f.read()
        content = await asyncio.to_thread(read_file)
        return content
    except FileNotFoundError:
        APP_LOGGER.error(f"template not found: {filename}")
        return None



async def send_response(writer, body, status_code=200, content_type="text/html"):
    response = (
        f"HTTP/1.1 {status_code} OK\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"{body}"
    )
    writer.write(response.encode())
    await writer.drain()

async def send_404(writer):
    content = await read_templates("404.html")
    if content is None:
        content = "404 Not Found"
        content_type = "text/plain"
    else:
        content_type = "text/html"
    await send_response(writer, content, status_code=404, content_type=content_type)

async def send_400(writer):
    body = "400 Bad Request"
    await send_response(writer, body, status_code=400, content_type="text/plain")

async def main():
    args = parse_args()
    server = await asyncio.start_server(handle_client, args.host, args.port)
    APP_LOGGER.info(f"Server started on {args.host}:{args.port}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        APP_LOGGER.info("Server shutown requested byuser")
