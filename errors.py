"""Handle any errors in Hactar"""
import traceback

from flask import current_app, render_template

@current_app.errorhandler(404)
def not_found(exc):
    """Handle HTTP not found error."""
    current_app.logger.debug('returning 404 error for: ' % exc.message)
    return render_template('error.html', exc=exc), 404

@current_app.errorhandler(500)
def internal_server_error(exc):
    """Handle internal server error."""
    current_app.logger.error('Unhandled error:\n' % traceback.format_exc())
    return render_template('error.html', exc=exc), 500
