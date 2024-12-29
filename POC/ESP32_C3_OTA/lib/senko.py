import requests
import uhashlib
import gc

class Senko:
    #raw = "http://raw.githubusercontent.com"
    github = "https://api.github.com/repos" #/alexphobby/Micropython/contents/POC/ESP32_C3_OTA/lib"
    github_raw = 'https://raw.githubusercontent.com' #/alexphobby/Micropython/main/POC/ESP32_C3_OTA/senko_test.py'
    def __init__(self, user, repo, url=None, branch="master", working_dir="app", files=["boot.py", "main.py"] , all_folder=False, headers={}):
        self.files = files
        self.all_folder = all_folder
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
        self.url = f'{self.github}/{user}/{repo}/contents/{working_dir}'
        self.url_raw = f'{self.github_raw}/{user}/{repo}/main/{working_dir}'
        #self.base_url = "{}/{}/{}".format(self.raw, user, repo) if user else url.replace(self.github, self.raw)
        #self.url = url if url is not None else "{}/{}/{}".format(self.base_url, branch, working_dir)
        self.headers = headers
        
        if "*" in files:
            print("Download all folder")
            self.all_folder = True
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
        print(f"url: {url}")
        payload = requests.get(url, headers={'User-Agent': 'alexphobby'})
        code = payload.status_code
        #print(f'_get_file code {code}, content: {payload.text}')

        if code == 200:
            #print(f"Got: {payload.text}")
            return payload.text
        else:
            print(f"Not ok, got http code: {code}")
            return None

    def _check_all(self):
        changes = []
        
        if self.all_folder:
            res = requests.get(self.url,headers = self.headers)
            if res.status_code != 200:
                print(f"Error loading github - {res.text}")
                return
            self.files = []
            for obj in res.json():
                if obj['type'] == 'dir':
                    print(f"Found folder {obj['name']} in repo")
                    _res = requests.get(f'{self.url}/{obj['name']}',headers = self.headers).json()
                    for _obj in _res:
                        if _obj['type'] == 'file':
                            print(f"Found file {_obj['name']} in {obj['name']}")
                            self.files.append(f'{obj['name']}/{_obj['name']}')
                else:
                    print(f"Found file {obj['name']} in repo")
                    self.files.append(obj['name'])
            res =""
            gc.collect()

        for file in self.files:
            print(f"Local check file: {file}")
            latest_version = self._get_file(self.url_raw + "/" + file)

            if latest_version is None:
                continue

            try:
                with open(file, "r") as local_file:
                    local_version = local_file.read()
            except:
                local_version = ""

            if not self._check_hash(latest_version, local_version):
                changes.append(file)

        return changes

    def fetch(self):
        pass
    
    def update(self):
        """Replace all changed files with newer one.

        Returns:
            True - if changes were made, False - if not.
        """
        changes = self._check_all()

        for file in changes:
            print(f'Write {file}')
            with open(file, "w") as local_file:
                
                local_file.write(self._get_file(self.url_raw + "/" + file))

        if changes:
            return True
        else:
            return False
