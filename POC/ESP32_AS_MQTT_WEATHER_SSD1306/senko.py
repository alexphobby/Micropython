import requests
import uhashlib
import gc

class Senko:
    raw = "http://raw.githubusercontent.com"
    github = "http://github.com"
    headers = {}

    def __init__(self, user, repo, url=None, branch="master", working_dir="app", files=["boot.py", "main.py"] , all_folder=False, headers={}):
        self.files = files
        
        self.all_folder = all_folder
        if len(headers) ==0:
            self.headers = {"User-Agent":user}
        else:
            self.headers = headers
            
        print(f"headers: {self.headers}")
        """Senko OTA agent class.

        Args:
            user (str): GitHub user.
            repo (str): GitHub repo to fetch.
            branch (str): GitHub repo branch. (master)
            working_dir (str): Directory inside GitHub repo where the micropython app is.
            url (str): URL to root directory.
            files (list): Files included in OTA update.
            headers (list, optional): Headers for urequests.
        """
        self.base_url = "{}/{}/{}".format(self.raw, user, repo) if user else url.replace(self.github, self.raw)
        self.url = url if url is not None else "{}/{}/{}".format(self.base_url, branch, working_dir)
        #self.headers = headers
        
        if "*" in files:
            print("Download all folder")
            self.all_folder = True
            self.files = []
        else:
            print("Download specific files")
            self.files = files

    def _check_hash(self, x, y):
        x_hash = uhashlib.sha1(x.encode())
        y_hash = uhashlib.sha1(y.encode())

        x = x_hash.digest()
        y = y_hash.digest()

        if str(x) == str(y):
            return True
        else:
            return False

    def _get_file(self, url):
        #print(f"url: {url}")
        gc.collect()
        payload = requests.get(url, headers=self.headers)
        code = payload.status_code
        text = payload.text
        gc.collect()

        if code == 200:
            return payload.text
        else:
            return None

    def _check_all(self):
        changes = []
        
        if self.all_folder:
            print(f"headers: {self.headers}")
            res = requests.get("http://api.github.com/repos/alexphobby/Micropython/contents/POC/ESP32_AS_MQTT_WEATHER_SSD1306",headers = self.headers).json()
            for obj in res:
                print(f"Found file {obj['name']} in repo")
                self.files.append(obj['name'])
            res =""
            gc.collect()

        for file in self.files:
            print(f"Local check file: {file}")
            latest_version = self._get_file(self.url + "/" + file)
            if latest_version is None:
                continue

            try:
                with open(file, "r") as local_file:
                    local_version = local_file.read()
            except:
                local_version = ""

            if not self._check_hash(latest_version, local_version):
                changes.append(file)
            gc.collect()

        return changes

    def fetch(self):
        """Check if newer version is available.

        Returns:
            True - if is, False - if not.
        """
        if not self._check_all():
            return False
        else:
            return True

    def update(self):
        """Replace all changed files with newer one.

        Returns:
            True - if changes were made, False - if not.
        """
        changes = self._check_all()

        for file in changes:
            with open(file, "w") as local_file:
                print(f"Write file {file}")
                local_file.write(self._get_file(self.url + "/" + file))
                gc.collect()

        if changes:
            return True
        else:
            return False
