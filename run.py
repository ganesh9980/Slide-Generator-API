from app import create_app
from app.utils.exceptions import handle_exception

app = create_app()
app.register_error_handler(Exception, handle_exception)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)