<h1>Job Finding Application in Flask</h1>
<h2>Created By Nikit Nagpara</h2>
<h4>Steps to download and run this project</h4>
<ol start="1">
<li>Download and Extract This Repository</li>
<li>Open command prompt in that folder</li>
<li>
   <p>Install Node Dependencies</p>

```bash
npm install
```
</li>
<li><p>Install virtualenv if you don't have it</p>  
    
```bash
pip install virtualenv
```

</li>
<li><p>create virtual environment for this project by using</p>

```bash
python -m venv .venv
```
<p align="center">OR</p>

```bash
virtualenv .venv
```
</li>
<li>
<p>Activate virtual environment</p>

```bash
.venv\Scripts\activate
```
</li>
<li>
<p>Install required dependencies</p>
    
```bash
pip install flask flask_mysqldb
```
</li>

<li>
<p>Setup Database</p>
<ul>
<li>Open XAMPP CONTROL PANEL.</li>
<li>Start <mark>Apache</mark> and <mark>MySQL</mark></li>
<li>Open <kbd>Admin</kbd> of MySQL</li>
<li>Create New Database as your wish Ex : "job_app"</li>
<li>Click on it then open <kbd>Import</kbd> Tab </li>
<li>SELECT file <code>job_app.sql</code>.
<li>Import tables by clicking <kbd>Import</kbd> button.</li>
</ul>
</li>
<li>
<p>Run the Project</p>

```bash
python app.py
```
</li>

</ol>
>>>>>>> 3cdd34975fc8e5b8d4db794471405a66cc0fb278
