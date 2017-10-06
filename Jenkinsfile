node("docker") {
    cleanWs()
    dir("code") {
        stage("Checkout") {
            scm_vars = checkout scm
        }
        
        stage("Create virtualenv") {
            sh "/usr/bin/scl enable rh-python35 'python3.5 -m venv build_env'"
        }
        
        stage("Install packets") {
            sh "scl enable rh-python35 'build_env/bin/pip install --upgrade pip'"
            sh "scl enable rh-python35 'build_env/bin/pip install -r requirements.txt'"
        }
    }
}