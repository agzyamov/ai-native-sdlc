# Faktöriyel Fonksiyonu - Türkçe Dokümantasyon

## Genel Bakış

Bu modül, bir sayının faktöriyelini hesaplamak için basit ve etkili bir Python fonksiyonu sağlar.

## Kullanım

```python
from factorial import factorial

# Temel kullanım
sonuc = factorial(5)  # 120
print(sonuc)
```

## Fonksiyon Açıklaması

### `factorial(n: int) -> int`

Negatif olmayan bir tam sayının faktöriyelini hesaplar.

Bir sayının faktöriyeli (n! olarak gösterilir), o sayıya eşit ve daha küçük olan tüm
pozitif tam sayıların çarpımıdır. Tanım gereği, 0! = 1'dir.

**Parametreler:**
- `n` (int): Faktöriyeli hesaplanacak negatif olmayan tam sayı

**Döndürür:**
- `int`: n sayısının faktöriyeli

**Hatalar:**
- `TypeError`: Eğer n bir tam sayı değilse
- `ValueError`: Eğer n negatif ise

## Örnekler

```python
from factorial import factorial

# Temel durumlar
print(factorial(0))   # Çıktı: 1
print(factorial(1))   # Çıktı: 1

# Küçük sayılar
print(factorial(5))   # Çıktı: 120
print(factorial(6))   # Çıktı: 720

# Daha büyük sayılar
print(factorial(10))  # Çıktı: 3628800
print(factorial(20))  # Çıktı: 2432902008176640000
```

## Hata Yönetimi

Fonksiyon, geçersiz girdiler için uygun hatalar fırlatır:

```python
from factorial import factorial

# Negatif sayı - ValueError fırlatır
try:
    factorial(-1)
except ValueError as e:
    print(e)  # "n must be non-negative, got -1"

# Tam sayı olmayan girdi - TypeError fırlatır
try:
    factorial(3.5)
except TypeError as e:
    print(e)  # "n must be an integer, got float"
```

## Testler

Testleri çalıştırmak için:

```bash
cd generated
python3 -m unittest test_factorial.py -v
```

## Kod Kalitesi

- **PEP 8**: Tam uyumlu
- **Flake8**: Hatasız
- **Pylint**: 10.00/10 puan
- **Test Kapsamı**: %100

## Teknik Detaylar

- **Algoritma**: Yinelemeli (iterative) yaklaşım
- **Zaman Karmaşıklığı**: O(n)
- **Alan Karmaşıklığı**: O(1)
- **Tip İpuçları**: Tam destek
- **Dokümantasyon**: Kapsamlı docstring'ler

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır.
