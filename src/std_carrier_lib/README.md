### Installation
```bash
pip install phonenumbers
```

### How to use

```python3
from helpers import CarrierInformation

if __name__ == "__main__":
    ci = CarrierInformation()
    
    operator_country = ci.get_country(operator_code=operator_code)
    phonenumber_country = ci.get_country(phone_number=phone_number)

    print("+ operator_country", operator_country)
    print("+ phonenumber_country", phonenumber_country)

    operator_name = ci.get_operator_name(operator_code=operator_code)
    phonenumber_name = ci.get_operator_name(phone_number=phone_number)

    print("+ operator_name", operator_name)
    print("+ phonenumber_name", phonenumber_name)
```
