#!groovy

node {

    try {
        stage 'Checkout'
            checkout scm

        stage 'Test'
            sh 'python3 -m venv venv'
            sh '. env/bin/activate'
            sh 'env/bin/pip install -r requirements.txt'
            sh 'python manage.py test'
    }

    catch (err) {
        sh "echo 'something has gone wrong'"

        throw err
    }

}
