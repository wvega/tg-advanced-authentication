<%inherit file="local:templates.master"/>
<%def name="title()">Login Form</%def>

<fb:login-button perms="email"></fb:login-button>

<div id="loginform">
<form action="${tg.url('/authenticate', params=dict(came_from=came_from.encode('utf-8'), __logins=login_counter.encode('utf-8')))}" method="POST" class="loginfields">
    <h2><span>Login</span></h2>
    <label for="login">Username:</label><input type="text" id="login" name="login" class="text"></input><br/>
    <label for="password">Password:</label><input type="password" id="password" name="password" class="text"></input>
    <input type="submit" id="submit" value="Login" />
</form>
</div>