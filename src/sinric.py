def send(value):
    # Replace with your Sinric API key
    api_key = "5176f8b7-0e16-429f-8f22-73d4093f7c40"
    app_secret = (
        "66c53efa-f3ce-419d-abe5-ac3fdecf71d9-4a0a01d2-5bd0-4ae1-806e-7c7a02438d73"
    )
    device_id = "63dec99f07e1833ecb5513d9"

    import socket

    # Criar socket
    s = socket.socket()

    # Conectar ao Sinric
    s.connect(("iot.sinric.com", 80))

    import utime

    while True:

        # Monta o pacote com os dados a serem enviados
        payload = (
            '{"deviceId": "'
            + device_id
            + '", "action": "setPowerState", "value": '
            + str(value)
            + ', "apikey": "'
            + api_key
            + '"}'
        )

        # Envia os dados para o Sinric
        s.send(payload.encode())

        # Recebe a resposta do Sinric
        data = s.recv(1024)

        # Imprime a resposta
        print(data.decode())

        # Aguarda alguns segundos antes de enviar novamente os dados
        utime.sleep(5)
