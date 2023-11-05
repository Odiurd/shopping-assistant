# Shopping Assistant
 
This program helps you track and receive notifications about discounts on your favorite products 
across various online grocery stores.

The primary purpose of this application is to focus on products with extended shelf lives. 
It allows you to take advantage of discounts and add these items to your online grocery cart, 
ensuring that you secure them at reduced prices rather than waiting until you deplete your stock 
and have to purchase them at the full price.

The current implementation is limited to Barbora and IKI (Lastmile) in Lithuania.

## Configuration
There are a few mandatory steps to set up the items to track and the notifications.

### Items to track
Define the items you want to track and be notified about. 
The app expects `items_to_track.tsv` in the `settings` folder, where the first row contains headers 
`item_name`, `item_url_suffix_barbora`, `item_url_suffix_iki`.

`item_name`: a name of your choice to identify the item. This must be unique.

`item_url_suffix_shopname`: the non-fixed part of the URL used to retrieve item information from the online store. 
`shopname` should be replaced with the tracker name, e.g. `barbora` or `iki`. 
When an item is not available in a specific store, leave the `item_url_suffix_shopname` empty.  


Below you can find an example with a missing item from Barbora. 
Please note that here we use `;` instead of tabs for easier readability but the file must be tabs-delimited.
```csv
item_name;item_url_suffix_barbora;item_url_suffix_iki
Coca cola zero bottle 1.5l;gazuotas-gerimas-coca-cola-zero-1-5-l-89167;Gazuotas-gerimas-COCA-COLA-ZERO-15-l
Coca cola zero bottle 1l;;Gazuotas-gaivusis-gerimas-COCA-COLA-ZERO-1-l
```

**For convenience, I recommend to build a Google Sheet with 
`ColumnA: item_name`, `ColumnB: item_url_suffix_barbora`, `ColumnC: item_url_suffix_iki` and to add one item per row.
The .tsv file can be generated easily by clicking on `File -> Download ->  Tab Separated Values (.tsv)`**

### Notifications
For email notifications, register to https://www.mailjet.com/ and obtain an API key and secret.

Then, create a `keys.yaml` file in `settings` folder. The file should look like this:

```yaml
MAILJET_API_KEY: <your_api_key>
MAILJET_API_SECRET: <your_api_secret>
```

You should also add the email addresses you will send emails from and to. 
This can be configured in `settings/personal_config.py`

```python
# replace the two emails below
FROM_EMAIL = "sender@gmail.com"
TO_EMAIL = "receiver@gmail.com"
```

### Optional settings
In `settings/config.py` you can change file locations and file names. 
Moreover, it is possible to change the template used for the email notification style.

## Scheduling
I host the application on a Raspberry Pi and schedule the two main jobs via `cron`. 
You should be able to use similar instructions on any Linux/MacOS device but I have not tested it.
Cloud hosting would require some extra changes which are not covered here for now.

- Make the `.sh` files in `scheduler/` folder executable.
    ```bash
    cd scheduler
    chmod +x run_extraction_job.sh
    chmod +x run_notify_job.sh
    ```
- Update the two files above to reflect your setup. 
I use a virtual environment named `venv` with [Poetry](https://python-poetry.org/docs/) for dependencies management.
- Run `crontab -e` and configure it to run extraction and notify jobs.
    ```bash
    # Example where the items are updated at 7 AM and a recap email is sent at 10.30 AM.
    
    0 7 * * * ~/<your-path-to-repository>/scheduler/run_extraction_job.sh >> ~/<your-path-to-repository>/scheduler/logs/cron_extraction.log
    30 10 * * * ~/<your-path-to-repository>/scheduler/run_notify_job.sh >> ~/<your-path-to-repository>/scheduler/logs/cron_notify.log
    ```
