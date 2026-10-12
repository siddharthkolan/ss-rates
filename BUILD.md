# App kaise banate hain (Claude ke naye session me)

Tools aur signing key kisi bhi session ke saath khatam ho jate hain. Naye session me:

1. Claude ko is repo tak access do (GitHub connect) aur **signing key backup file** (`SS-Rates-signing-key-BACKUP.txt`) attach karo.
2. Claude ye chalata hai:
   ```
   git clone https://github.com/siddharthkolan/ss-rates
   # backup file ko key.pem aur cert.pem me todna: ssrates.key.pem / ssrates.cert.pem -> source/../out/
   SS_TOOLS=/kuch/folder python3 source/setup_tools.py
   SS_TOOLS=/kuch/folder python3 source/release.py --bump 2.7 --notes "..." --push
   ```
3. `release.py` version, signing key (fingerprint), signature, dex sab check karti hai. Koi check fail ho to upload nahi hota.

Signing key kabhi is repo me commit mat karo (repo public hai).
Key khoyi to purane install par update nahi chadhega; purana app uninstall karke naya install karna padega.
