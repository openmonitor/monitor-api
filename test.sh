pip3 install pytest
pip3 install pytest-cov
pip3 install pytest-mock-server
pip3 install pytest-docker
export PYTHONPATH=$PYTHONPATH:.
pytest ./test --cov=./monitor_api