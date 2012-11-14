==========================================
 Web Spider pro parlamentní data z psp.cz
==========================================

*Note:* The following texts are in Czech as I do not expect any interest from
foreigners about this project. But if I prove wrong, do not hesitate to contact
me directly.

Tento projekt implementuje Scrapy spidery (pavouky), kteří prochází web
Poslanecké sněmovny České republiky (psp.cz) a ukládají získané informace
ve strukturované formě do databáze. Projekt je rozdělen na 2 pavouky -
*psp.cz* pavouk získává informace o proběhlých hlasováních v poslanecké sněmovně
a *poslanci.psp.cz* ukládá informace o poslancích. Rozdělení je z toho
důvodu, že zatímco informace o hlasování je vhodné aktualizovat na denní bázi,
pro informace o poslancích toto není nutné.

Použití
=======
Před spuštěním je potřeba nastavit následující systémové proměnné:
- DATABASE_URL - url pro připojení do databáze, například
postgresql://user:pass@128.0.0.1:5432/database
- IMAGES_STORE - adresář, kam se budou ukládat obrázky poslanců. Toto nastavení
používá pavouk poslanci.psp.cz

Samotné spuštění pavouka je příkazem::
    scrapy crawl psp.cz
případně::
    scrapy crawl poslanci.psp.cz

Pavouk psp.cz
=============
Pavouk ukládá informace o hlasování v poslanecké směnovně. Pro informaci
o použitém databázovém schématu se podívejte do souboru psp_cz_models.py. Pavouk
podporuje následující parametry:
- **mode**:
  Povolené hodnoty jsou buď *incremental* (default) nebo *full*. Full
  mode kompletně stáhne informace o hlasování z aktuálního období.
  Incremental provede aktualizaci posledního zasedání v databázi a
  přidá všechna nová chybějící. K inkrementálnímu módu se vztahují
  další 2 parametry - from_term a from_sitting.
- **from_term**:
  Specifikuje období, od kterého se má začít s parsováním údajů. Zároveň
  musí být nastavený parametetr *from_sitting*.
  *Upozornění:* Parsování jiných období než aktuálního (6. volební období)
  není otestované a je možné, že obsahuje chyby.
- **from_sitting**:
  Specifikuje číslo zasedání sněmovny. Je nutné jej použít v kombinaci s
  parametrem *from_term*.

Příklad použití se všemi parametry::
    scrapy crawl psp.cz -a mode=incremental -a from_term=6 -a from_sitting=40

Pavouk poslanci.psp.cz
======================
Pavouk stahuje informace o poslancích parlamentu ČR. Jedná se hlavně o
příslušnost k politické straně, regionu a fotografii. Tento pavouk nepoužívá
žádné parametry. Ke správné funkci stahování obrázků je potřeba správně nastavit
systémovou proměnnou IMAGES_STORE - například D:/poslanci/images/. Pro přiřazení
obrázku poslance k databázovému záznamu v tabulce *parl_memb* je třeba použít
sloupec *picture_hash* - obsahuje jméno souboru bez přípony.

Příklad použití::
    scrapy crawl poslanci.psp.cz
