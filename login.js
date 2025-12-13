/**
 * Login Page - Smart Financial Advisor
 * With Authentication API Integration
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Login page loaded');

    // ========================================
    // Form Toggle - Login/Register
    // ========================================
    var loginContainer = document.getElementById('loginContainer');
    var registerContainer = document.getElementById('registerContainer');
    var showRegisterBtn = document.getElementById('showRegister');
    var showLoginBtn = document.getElementById('showLogin');

    if (showRegisterBtn && loginContainer && registerContainer) {
        showRegisterBtn.addEventListener('click', function(e) {
            e.preventDefault();
            loginContainer.style.display = 'none';
            registerContainer.style.display = 'block';
        });
    }

    if (showLoginBtn && loginContainer && registerContainer) {
        showLoginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            registerContainer.style.display = 'none';
            loginContainer.style.display = 'block';
        });
    }

    // ========================================
    // Form Handling - Login with API
    // ========================================
    var loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            var email = document.getElementById('email').value;
            var password = document.getElementById('password').value;
            var submitBtn = loginForm.querySelector('button[type="submit"]');
            var originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = 'Signing in...';
            submitBtn.disabled = true;
            
            try {
                var response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email, password: password }),
                    credentials: 'include'
                });
                
                var data = await response.json();
                
                if (response.ok) {
                    // Store user info in localStorage
                    localStorage.setItem('user', JSON.stringify(data.user));
                    window.location.href = '/';
                } else {
                    alert(data.detail || 'Login failed');
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('Login failed. Please try again.');
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // ========================================
    // Form Handling - Register with API
    // ========================================
    var registerForm = document.getElementById('registerForm');

    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            var name = document.getElementById('regName').value;
            var email = document.getElementById('regEmail').value;
            var password = document.getElementById('regPassword').value;
            var confirm = document.getElementById('regConfirm').value;
            var submitBtn = registerForm.querySelector('button[type="submit"]');
            var originalText = submitBtn.innerHTML;
            
            if (password !== confirm) {
                alert('Passwords do not match!');
                return;
            }
            
            if (password.length < 6) {
                alert('Password must be at least 6 characters');
                return;
            }
            
            submitBtn.innerHTML = 'Creating account...';
            submitBtn.disabled = true;
            
            try {
                var response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name, email: email, password: password })
                });
                
                var data = await response.json();
                
                if (response.ok) {
                    alert('Account created! Please sign in.');
                    registerContainer.style.display = 'none';
                    loginContainer.style.display = 'block';
                    // Pre-fill email
                    document.getElementById('email').value = email;
                } else {
                    alert(data.detail || 'Registration failed');
                }
            } catch (error) {
                console.error('Registration error:', error);
                alert('Registration failed. Please try again.');
            }
            
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    }

    // ========================================
    // Google Button (Demo - redirect to main)
    // ========================================
    var googleBtn = document.querySelector('.btn-social.google');
    if (googleBtn) {
        googleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Google OAuth not configured. Use email/password or demo account:\n\nEmail: demo@example.com\nPassword: demo123');
        });
    }

    // ========================================
    // GitHub Button (Demo - redirect to main)
    // ========================================
    var githubBtn = document.querySelector('.btn-social.github');
    if (githubBtn) {
        githubBtn.addEventListener('click', function(e) {
            e.preventDefault();
            alert('GitHub OAuth not configured. Use email/password or demo account:\n\nEmail: demo@example.com\nPassword: demo123');
        });
    }

    // ========================================
    // Entrance Animation
    // ========================================
    var cards = document.querySelectorAll('.bento-card');
    for (var j = 0; j < cards.length; j++) {
        (function(index) {
            cards[index].style.opacity = '0';
            cards[index].style.transform = 'translateY(30px)';
            setTimeout(function() {
                cards[index].style.transition = 'all 0.5s ease';
                cards[index].style.opacity = '1';
                cards[index].style.transform = 'translateY(0)';
            }, 100 + index * 100);
        })(j);
    }

    // ========================================
    // Check if already logged in
    // ========================================
    fetch('/api/auth/check', { credentials: 'include' })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.authenticated) {
                window.location.href = '/';
            }
        })
        .catch(function(err) { console.log('Auth check:', err); });

});
