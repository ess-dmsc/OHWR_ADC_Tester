# OHWR ADC Tester
This is project to be used for testing of the KU040 FPGA demo board running firmware which reads data from the OHWR 14-bit. If there is something in that previous sentence that you are not aware of, this project is not for you.


```bash
python3.6 -m venv build_env
source ./build_env/bin/activate
pip install -r requirements.txt
pyinstaller -w OHWR_ADC_Tester.py
tar czvf OHWR_ADC_Tester.tar.gz -C dist/ OHWR_ADC_Tester/
tar xzvf OHWR_ADC_Tester.tar.gz
```