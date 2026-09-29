# batchReals

Script hors APK. Il lit une liste `code;prénom;nom;nom affiché`, interroge TMDB
et écrit `{CODE}.jpg` dans `output/photos/` plus les biographies dans
`output/bios.json`.

La clé est celle de `batchsData/batchPosters/.env` (`TMDB_API_KEY`), ou un
`.env` local dans ce dossier.

```powershell
cd D:\Programs\Android_Studio\projets\Urbinema\batchsData\batchReals
python reals_batch.py generate
python reals_batch.py fetch --limit 5
python reals_batch.py all
```

Une personne n’est gardée que si le nom TMDB (ou un alias) correspond au nom
du catalogue. Les photos déjà présentes ne sont pas retéléchargées.
