from flask import Blueprint, render_template

# =============================================================================
# TEMPORARY USER AUTHENTICATION MODULE - TO BE REPLACED
# =============================================================================
# WARNING: This is a placeholder implementation that will be removed once 
# the proper user management module is implemented.
# It provides minimal routing to prevent template errors with current_user.
# =============================================================================
user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/account")
def account():
    return render_template("error.html", 
                          code=501, 
                          title="Not Implemented",
                          heading="Feature Not Implemented", 
                          details="User account is not yet available.")

# =============================================================================
# END OF TEMPORARY USER AUTHENTICATION MODULE
# =============================================================================
