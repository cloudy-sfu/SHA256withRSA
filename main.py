import pywebio
import sha256withrsa

with open('html/main.html', 'r') as f:
    html_main = f.read()
with open('html/nav.html', 'r') as f:
    html_nav = f.read()


def validate_n(n):
    if n < 1024:
        return 'The number should be greater or equal to 1024.'


def index():
    pywebio.output.clear()
    pywebio.output.put_html(html_main)


def generate():
    pywebio.output.put_html(html_nav)
    data = pywebio.input.input_group("Generate keypair", [
        pywebio.input.input(label='Key name', name='filename', value='id_rsa', required=True),
        pywebio.input.input(label='Complexity', name='n', value='2048', required=True, type='number',
                            validate=validate_n, help_text='Minimum complexity is 1024.'),
    ])
    private_key, public_key = sha256withrsa.generate(n=data['n'])
    pywebio.output.put_markdown('# Download')
    pywebio.output.put_file(name=data['filename'], content=private_key, label='Private key')
    pywebio.output.put_file(name=data['filename'] + '.pub', content=public_key, label='Public key')


def sign():
    pywebio.output.put_html(html_nav)
    data = pywebio.input.input_group("Sign message", [
        pywebio.input.textarea(label='Message', name='content', required=True),
        pywebio.input.file_upload(label='Private key', name='private', required=True),
    ])
    pywebio.output.put_markdown('# Signature')
    signature = sha256withrsa.sign(data['content'], data['private']['content'])
    if signature:
        pywebio.output.put_text(signature)
    else:
        pywebio.output.put_error('The private key is invalid. This error may also appear if you use a public key '
                                 'to sign a message.')


def verify():
    pywebio.output.put_html(html_nav)
    data = pywebio.input.input_group("Verify signature", [
        pywebio.input.textarea(label='Message', name='content', required=True),
        pywebio.input.textarea(label='Signature', name='signature', required=True),
        pywebio.input.file_upload(label='Public key', name='public', required=True),
    ])
    result = sha256withrsa.verify(content=data['content'], signature=data['signature'],
                                  public_key=data['public']['content'])
    pywebio.output.put_markdown('# Result')
    if result:
        pywebio.output.put_success("VALID. This message is from the holder of the corresponding private key.")
    else:
        pywebio.output.put_error("INVALID. This signature does not match the message, or is not generated from"
                                 "the corresponding private key which pairs your public key.")


def encrypt():
    pywebio.output.put_html(html_nav)
    data = pywebio.input.input_group("Encrypt message", [
        pywebio.input.textarea(label='Message', name='content', required=True),
        pywebio.input.file_upload(label='Public key', name='public', required=True),
    ])
    encrypted_content = sha256withrsa.encrypt(data['content'], data['public']['content'])
    pywebio.output.put_markdown('# Encrypted content')
    pywebio.output.put_html('<p style="color: red"><i>Please send everything inside the curly braces (including the '
                            'curly braces themselves) to your contact.</i></p>')
    if encrypted_content:
        pywebio.output.put_text(encrypted_content)
    else:
        pywebio.output.put_error('The public key is invalid.')


def decrypt():
    pywebio.output.put_html(html_nav)
    data = pywebio.input.input_group("Decrypt message", [
        pywebio.input.textarea(label='Encrypted content', name='content', required=True,
                               help_text='Please paste everything inside the curly braces (including the curly braces '
                                         'themselves) here.'),
        pywebio.input.file_upload(label='Private key', name='public', required=True),
    ])
    message = sha256withrsa.decrypt(data['content'], data['public']['content'])
    pywebio.output.put_markdown('# Message')
    if message:
        pywebio.output.put_text(message)
    else:
        pywebio.output.put_error('The message is corrupted, or the private key is invalid.')


if __name__ == '__main__':
    # Debug
    # pywebio.start_server([index, generate, sign, verify, encrypt, decrypt], auto_open_webbrowser=False, port=5000,
    #                      debug=True)
    # Deploy
    pywebio.start_server([index, generate, sign, verify, encrypt, decrypt], auto_open_webbrowser=True)
