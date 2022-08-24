# Fix creation date

Utility to set creation time for your transmission torrent library.

now works only for *Windows*
Takes time from `addedDate` field, refer to [rpc-spec](https://github.com/transmission/transmission/blob/main/docs/rpc-spec.md),
set it to folders/files upper level.

to make non-dry run call `main(dry_run=False)`.


## cfg.ini example
```

[default]
url=http://127.0.0.1:9091/transmission/rpc/

[auth]
login=***
password=***
XV=*** your csrf token, 48 alphanum chars ***
```
