# Required for the image validation as explained here: https://REDACTED.redhat.com/docs/DOC-000#jive_content_id_Common_tests
# Must be in the root folder of the repo; will not be recognized in the context directory
@has_s2i_base = true
@create_options = { 'entrypoint' => '/bin/bash', }
