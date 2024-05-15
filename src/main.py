import os
import hashlib
import re
from datetime import datetime

def ensure_dir_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def normalize(name):
    """Normalize package names according to the specification."""
    return re.sub(r"[-_.]+", "-", name).lower()

def generate_file_hash(file_path, hash_function="sha256"):
    """Generate a hash for the file."""
    hash_func = hashlib.new(hash_function)
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def update_root_index(index_path, package_name):
    try:
        # Read the existing index data
        if os.path.exists(index_path):
            with open(index_path, 'r') as file:
                index_html = file.read()
        else:
            index_html = "<!DOCTYPE html><html><body></body></html>"

        # Check if the package name already exists in the index
        if f'href="/{package_name}/"' not in index_html:
            # Insert the new package link before the closing body tag
            index_html = index_html.replace("</body>", f'<a href="/{package_name}/">{package_name}</a></body>')
        
        # Write the updated index data back to the file
        with open(index_path, 'w') as file:
            file.write(index_html)
        
        print(f"Upserted {package_name} into index successfully.")
    except Exception as e:
        print(f"An error occurred while upserting the index: {e}")

def update_package_index(package_dir, package_name, version, archive_url):
    try:
        print("update_package_index:")
        print(f"package_dir: {package_dir}")
        print(f"package_name: {package_name}")
        print(f"version: {version}")
        print(f"archive_url: {archive_url}")

        # Ensure the package directory exists
        print(f"Ensuring package directory {package_dir} exists.")
        ensure_dir_exists(package_dir)
        package_index_path = os.path.join(package_dir, "index.html")
        print(f"Updating package index at {package_index_path}.")

        # Generate the hash value for the archive URL
        hash_value = generate_file_hash(archive_url)
        link = f"<a href='{archive_url}#sha256={hash_value}'>{archive_url}</a>"
        version_info = f"({version}, {datetime.now().isoformat()})"
        print(f"Link: {link}")
        print(f"Version info: {version_info}")

        # Read the existing HTML content if the file exists
        print(f"Reading existing package index at {package_index_path}.")
        if os.path.exists(package_index_path):
            with open(package_index_path, 'r') as file:
                index_html = file.read()
            
            # Check if the version is already listed in the HTML content
            if link not in index_html:
                # Insert the new link and version info before the closing ul tag
                index_html = index_html.replace("</ul>", f"<li>{link} {version_info}</li></ul>")
        else:
            # Create new HTML content if the file doesn't exist
            index_html = f"""<!DOCTYPE html>
<html>
    <head>
        <title>{package_name}</title>
    </head>
    <body>
        <h1>{package_name}</h1>
        <p>Generated on {datetime.now().isoformat()}.</p>
        <ul>
            <li>{link} {version_info}</li>
        </ul>
    </body>
</html>"""

        # Write the updated or new HTML content to the file
        with open(package_index_path, 'w') as file:
            file.write(index_html)
        
        print(f"Upserted version {version} into {package_dir} successfully.")
    except Exception as e:
        print(f"An error occurred while upserting the package index: {e}")

def upsert_package(root_dir, package_name, version, archive_url):
    package_name_normalized = normalize(package_name)
    print(f"Upserting package {package_name_normalized} version {version} from {archive_url}.")

    # ensure the root directory exists
    print(f"Ensuring root directory {root_dir} exists.")
    ensure_dir_exists(root_dir)

    # update the root index
    print(f"Updating root index at {os.path.join(root_dir, 'index.html')}.")
    update_root_index(os.path.join(root_dir, "index.html"), package_name_normalized)


    package_dir = os.path.join(root_dir, package_name_normalized)
    update_package_index(package_dir, package_name_normalized, version, archive_url)

# # Example usage
# root_dir = 'pypi'
# package_name = 'foo'
# version = '1.0.0'
# archive_url = 'https://github.com/path/to/archive.tgz'

# upsert_package(root_dir, package_name, version, archive_url)

# set up main
if __name__ == "__main__":

    # env vars:
    # root_dir
    # python_service_name
    # python_service_version
    # python_service_archive_url
    root_dir = os.environ.get('root_dir')
    package_name = os.environ.get('python_service_name')
    version = os.environ.get('python_service_version')
    archive_url = os.environ.get('python_service_archive_url')

    upsert_package(root_dir, package_name, version, archive_url)