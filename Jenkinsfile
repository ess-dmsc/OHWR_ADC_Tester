node("docker") {
    cleanWs()
    dir("code") {
        stage("Checkout") {
            scm_vars = checkout scm
        }
        
        stage("Create virtualenv") {
            sh "/usr/bin/scl enable rh-python35 /bin/bash & python3.5 -m venv build_env"
        }
    }
}