# ps2-bankmod-batch
Extracts and replaces samples within PlayStation 2 .HD/.BD banks. This small tweak of the [original script](https://github.com/Nisto/ps2-bankmod) by **[Nisto](https://github.com/Nisto)** makes it easy to import a lot of samples at once.

## Usage
To extract all VAG samples from an .HD/.BD bank pair:
```
ps2-bankmod-batch.py -e INPUT.hd INPUT.bd OutputDirectory
```
To import all VAG samples present in a directory into an .HD/.BD bank:
```
ps2-bankmod-batch.py -i INPUT.hd INPUT.bd ImportsDirectory
```

#### Batching
You can also use `.bat` files or CMD to, for example, extract all .HD/.BD banks present in the same directory as `ps2-bankmod-batch.py`:
```
for %%1 in (*.hd) do ps2-bankmod-batch.py -e "%%~n1.hd" "%%~n1.bd" "%%~n1"
```
...and to mass-import new VAG samples into .HD/.BD banks from their associated folders:
```
for %%1 in (*.hd) do ps2-bankmod-batch.py -i "%%~n1.hd" "%%~n1.bd" "%%~n1"
```
※ Just make sure that .HD/.BD pairs have the same basename (e.g.: `file.hd` & `file.bd`, not `abc.hd` & `xyz.bd`).

## Notes
- Be sure to keep the VAG filenames in the output/imports directories as they are, as this version of the script picks up imported VAGs' index numbers for .HD/.BD based on their filenames.
- For imports, it's not necessary to keep the VAG samples that you don't need to change within .HD/.BD banks – you're free to remove them from output/imports directories if you'd like to.

---
Just to be clear, the bottom section of this readme.md stayed as it was in the original repo. Do support Nisto if you value their work; for example, this script was an invaluable tool in putting together many PS2 mods on my end.

## Support ❤️

As of June 2024, my monthly salary has been cut by 50%. This has had a significant impact on my freedom and ability to spend as much time working on my projects, especially due to electricity bills. I don't like asking for favors or owing people anything, but if you do appreciate this work and happen to have some funds to spare, I would greatly appreciate any and all donations. All of your contributions goes towards essential everyday expenses. Every little bit helps! Thank you ❤️

**PayPal:** https://paypal.me/nisto7777  
**Buy Me a Coffee:** https://buymeacoffee.com/nisto  
**Bitcoin:** 18LiBhQzHiwFmTaf2z3zwpLG7ALg7TtYkg
