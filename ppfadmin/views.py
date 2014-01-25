from flask.ext.login import login_user
from flask import flash, render_template, url_for, redirect


from .models import LoginForm, RegistrationForm
from .models import User

from ppf.viewer import JinjaEnvironment
from dlibs.logger import loggero

from flask import app


from flask import Flask


def ppfadmin_login(request):
    form = LoginForm(request.form)
    next_uri = request.args.get("next")
    form.next = next_uri
    print(form.next, next_uri)

    if form.validate():
        user = form.get_user()        
        login_user(user)
        flash("Logged in sucessfully.")
        return redirect(request.args.get("next") or url_for('home'))

    return JinjaEnvironment().get_template('admin/login.html').render(form=form)

def ppfadmin_join(request):
    form = RegistrationForm(request.form)
    next_uri = request.args.get("next")
    form.next = next_uri
    print(next_uri, form.next)
    
    if form.validate():
        user = User()
        user.email = form.email.data
        user.password = form.password.data
        user.save()
        login_user(user)
        flash("Logged in sucessfully.")        
        return redirect(request.args.get("next") or url_for('home'))
    return JinjaEnvironment().get_template('admin/registration.html').render(form=form)
