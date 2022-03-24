import pywebio
import sha256withrsa


def index():
    pywebio.output.put_markdown(
        """
        # SHA256withRSA
        **Verify signature**: 
        Given the content and signature, use the public key to verify if the signature is valid.
        <center><a href="/?app=verify">Enter</a></center>
        
        **Generate**:
        Generate a SHA256withRSA keypair, including a public key and a private key.
        <center><a href="/?app=generate">Enter</a></center>
        
        **Sign**:
        Given the content, use the private key to sign it.
        <center><a href="/?app=sign">Enter</a></center>
        
        <hr>
        
        Authored by [cloudy-sfu](https://github.com/cloudy-sfu/), 2022.
        """
    )


def verify():
    pywebio.output.put_html('<a href="/?app=index">Back</a> to the index page.')
    data = pywebio.input.input_group("Verify signature", [
        pywebio.input.textarea(label='Text content', name='content', required=True),
        pywebio.input.textarea(label='Signature', name='signature', required=True),
        pywebio.input.file_upload(label='Public key', name='pub', required=True),
    ])

    result, message = sha256withrsa.verify(
        content=data['content'],
        signature=data['signature'],
        public_key_=data['pub']['content']
    )

    pywebio.output.put_table([['Name', 'Value'], ['Valid?', result], ['Message', message]])


def generate():
    pywebio.output.put_html('<a href="/?app=index">Back</a> to the index page.')
    data = pywebio.input.input_group("Generate keypair", [
        pywebio.input.input(label='Key name', name='filename', required=True),
        pywebio.input.input(label='Complexity [optional]', name='n', required=False, type='number'),
    ])

    private_key, public_key = sha256withrsa.generate(n=data['n'])

    pywebio.output.put_markdown('## Download')
    pywebio.output.put_row([
        pywebio.output.put_file(name=data['filename'], content=private_key, label='Private key'),
        pywebio.output.put_file(name=data['filename'] + '.pub', content=public_key, label='Public key')
    ])


def sign():
    pywebio.output.put_html('<a href="/?app=index">Back</a> to the index page.')
    data = pywebio.input.input_group("Verify signature", [
        pywebio.input.textarea(label='Text content', name='content', required=True),
        pywebio.input.file_upload(label='Private key', name='private', required=True),
    ])

    signature, message = sha256withrsa.sign(content=data['content'], private_key_=data['private']['content'])

    pywebio.output.put_table([['Name', 'Value'], ['Signature', signature], ['Message', message]])


if __name__ == '__main__':
    # Debug
    # pywebio.start_server([index, verify, generate, sign], auto_open_webbrowser=False, port=5000)
    # Deploy
    pywebio.start_server([index, verify, generate, sign], auto_open_webbrowser=True)
