# Mailing

## Backends

### WhitelistEmailBackend

In some cases it is useful to debug and test email functionality on local or test environments. Additionally, your
project could contain logic, that triggers emails in the background, so it is very important, that you don't send emails
to other domains, e.g. 'xyz@test.de' or to other test users with another domain, by accident.

This email backend can be used as Django EMAIL_BACKEND to restrict outgoing emails to a set of allowed domains. You can
define an email address (must be a catchall inbox), where the restricted emails should be redirected to.

Example:

    EMAIL_BACKEND = 'ambient_toolbox.mail.backends.whitelist_smtp.WhitelistEmailBackend'
    EMAIL_BACKEND_DOMAIN_WHITELIST = ['ambient.digital']
    EMAIL_BACKEND_REDIRECT_ADDRESS = '%s@testuser.ambient.digital'

If EMAIL_BACKEND_REDIRECT_ADDRESS is configured, an email to 'albertus.magnus@example.com' will be redirected to:
albertus.magnus_example.com@testuser.ambient.digital
