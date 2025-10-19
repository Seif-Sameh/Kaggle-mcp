import os, json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import asyncio


load_dotenv()


# Create an MCP server
mcp = FastMCP("kaggle-mcp")


def init_kaggle():
    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_API_KEY")

    if not username or not key:
        raise ValueError("Missing KAGGLE_USERNAME or KAGGLE_KEY environment variables")

    creds = {"username": username, "key": key}
    kaggle_dir = os.path.expanduser("~/.kaggle")
    kaggle_path = os.path.join(kaggle_dir, "kaggle.json")

    os.makedirs(kaggle_dir, exist_ok=True)
    with open(kaggle_path, "w") as f:
        json.dump(creds, f)
    os.chmod(kaggle_path, 0o600)



#---------------
# Competitions
#---------------


@mcp.tool()
async def competitions_list(page: int = 1, search: str = None) -> dict:
    """List Kaggle competitions with optional filtering.

    Parameters
    ----------
    page : int, optional
        Page number to retrieve (default: 1)
    search : str, optional
        Search term to filter results

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "competitions": list  # Present only on success
        }
    """
    try:
        loop = asyncio.get_running_loop()
        comps = await loop.run_in_executor(None, lambda: api.competitions_list(page=page, search=search))
        return {
            "status": "success",
            "message": f"Retrieved {len(comps)} competitions.",
            "competitions": [c.ref for c in comps],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def competition_list_files(competition: str, page_token: str = None, page_size: int = 20) -> dict:
    """List files available in a Kaggle competition.

    Parameters
    ----------
    competition : str
        Competition identifier or name
    page_token : str, optional
        Pagination token (default: None)
    page_size : int, optional
        Number of files per page (default: 20, range: 1–100)

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "files": list (only if success)
        }
    """
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, lambda: api.competition_list_files(competition, page_token=page_token, page_size=page_size)
        )
        return {
            "status": "success",
            "message": f"Retrieved {len(result.files)} files for '{competition}'.",
            "files": [f for f in result.files],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def competition_download_file(competition: str, file_name: str, path: str = None, force: bool = False, quiet: bool = True) -> dict:
    """Download a specific file from a Kaggle competition.

    Parameters
    ----------
    competition : str
        Competition identifier or name
    file_name : str
        Name of the file to download
    path : str, optional
        Local directory to save the file (default: current directory)
    force : bool, optional
        Overwrite existing file if True (default: False)
    quiet : bool, optional
        Suppress progress messages if True (default: True)

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "competition": str,
            "file_name": str,
            "saved_path": str (only if success)
        }
    """
    try:
        import os
        save_path = path or os.getcwd()

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: api.competition_download_file(
                competition, file_name, path=save_path, force=force, quiet=quiet
            ),
        )

        return {
            "status": "success",
            "message": f"File '{file_name}' from '{competition}' downloaded successfully.",
            "competition": competition,
            "file_name": file_name,
            "saved_path": os.path.abspath(save_path),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def competition_download_files(competition: str, path: str = None, force: bool = False, quiet: bool = True) -> dict:
    """Download all files from a Kaggle competition.

    Parameters
    ----------
    competition : str
        Competition identifier or name
    path : str, optional
        Local directory to save files (default: current directory)
    force : bool, optional
        Overwrite existing files if True (default: False)
    quiet : bool, optional
        Suppress progress messages if True (default: True)

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "competition": str,
            "saved_path": str (only if success)
        }
    """
    try:
        import os
        save_path = path or os.getcwd()

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: api.competition_download_files(
                competition, path=save_path, force=force, quiet=quiet
            ),
        )

        return {
            "status": "success",
            "message": f"Downloaded all files for competition '{competition}'.",
            "competition": competition,
            "saved_path": os.path.abspath(save_path),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def competition_submit(file_name: str, message: str, competition: str, quiet: bool = False) -> dict:
    """Submit a file to a Kaggle competition.

    Parameters
    ----------
    file_name : str
        Path to the submission file
    message : str
        Description or notes for the submission
    competition : str
        Competition identifier or name
    quiet : bool, optional
        Suppress progress messages if True (default: False)

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "competition": str,
            "submission_ref": str (only if success)
        }
    """
    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: api.competition_submit(file_name, message, competition, quiet=quiet)
        )

        if hasattr(response, "to_dict"):
            response_dict = response.to_dict()
        else:
            response_dict = response.__dict__
        

        return {
            "status": "success",
            "message": response_dict.get("message"),
            "competition": competition,
            "submission_ref": response_dict.get("ref"),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def competition_submissions(competition: str, group: str = None, sort: str = None, page_token: int = 0, page_size: int = 20) -> dict:
    """Get a list of all the submissions for a particular competition.

    Parameters
    ----------
    competition : str
        The unique identifier or name of the competition
    group : str, optional
        Filter submissions by group. Valid groups include:
        - 'general' - Default competition submissions
        - 'entered' - Only submissions you have entered
        - 'community' - Community competition submissions
        - 'hosted' - Hosted competition submissions
        - 'unlaunched' - Unlaunched competition submissions
        - 'unlaunched_community' - Unlaunched community competition submissions
        Default: None (no group filtering)
    sort : str, optional
        How to sort the results. Valid sorting options:
        - 'grouped' - Group by custom criteria
        - 'best' - Sort by best score
        - 'prize' - Sort by prize amount
        - 'earliestDeadline' - Sort by earliest deadline first
        - 'latestDeadline' - Sort by latest deadline first
        - 'numberOfTeams' - Sort by number of teams
        - 'relevance' - Sort by relevance
        - 'recentlyCreated' - Sort by creation date
        Default: None (default sorting)
    page_token : int, optional
        Token for paginating through results when there are multiple pages
        Default: 0
    page_size : int, optional
        Number of submissions to return per page
        Default: 20
        Range: 1-100

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "competition": str,
            "data": list (only if success)
        }

    Notes
    -----
    This API call requires authentication with appropriate permissions for the competition.
    """
    try:
        loop = asyncio.get_running_loop()
        submissions = await loop.run_in_executor(
            None,
            lambda: api.competition_submissions(competition, group, sort, page_token, page_size)
        )

        return {
            "status": "success",
            "message": f"Retrieved {len(submissions)} submissions.",
            "competition": competition,
            "data": [s.to_dict() if hasattr(s, "to_dict") else s.__dict__ for s in submissions],
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def competition_leaderboard_view(competition: str) -> dict:
    """Retrieve the current leaderboard for a Kaggle competition.

    Parameters
    ----------
    competition: str
        The unique identifier or name of the competition

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "competition": str,
            "data": list (only if success)
        }
    """
    try:
        loop = asyncio.get_running_loop()
        leaderboard = await loop.run_in_executor(
            None, lambda: api.competition_leaderboard_view(competition)
        )

        return {
            "status": "success",
            "message": f"Retrieved {len(leaderboard)} leaderboard entries.",
            "competition": competition,
            "data": [entry.to_dict() if hasattr(entry, "to_dict") else entry.__dict__ for entry in leaderboard],
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def competition_leaderboard_download(competition: str, path: str, quiet: bool = True) -> dict:
    """Download the leaderboard data for a Kaggle competition to a local file.

    Parameters
    ----------
    competition: str
        The unique identifier or name of the Kaggle competition to download the leaderboard from.
    path: str
        The local file system path where the leaderboard file should be saved.
    quiet: bool, optional
        If True, suppresses progress messages and status updates during download.
        Default: True

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "competition": str
        }
    """
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, lambda: api.competition_leaderboard_download(competition, path, quiet=quiet)
        )
        return {
            "status": "success",
            "message": f"Downloaded leaderboard for competition: {competition} to path: {path or os.getcwd()}",
            "competition": competition,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


#-----------
# Datasets
#-----------


@mcp.tool()
async def datasets_list(sort_by=None, size=None, file_type=None, license_name=None, tag_ids=None, search=None, user=None, mine=False, page=1, max_size=None, min_size=None) -> dict:
    """Return a list of datasets.

    Parameters
    ----------
    sort_by: str
        How to sort the result. Valid options are:
        - 'hottest': Sort by trending/popularity
        - 'votes': Sort by number of votes
        - 'updated': Sort by last update date
        - 'active': Sort by active status
        - 'published': Sort by publication date

    file_type: str
        The format of datasets to filter by. Valid options are:
        - 'all': Show all file types
        - 'csv': Show only CSV files
        - 'sqlite': Show only SQLite databases
        - 'json': Show only JSON files
        - 'bigQuery': Show only BigQuery datasets

    license_name: str
        License type to filter by. Valid options are:
        - 'all': Show all licenses
        - 'cc': Show Creative Commons licenses
        - 'gpl': Show GPL licenses
        - 'odb': Show Open Database licenses
        - 'other': Show other licenses

    tag_ids: list
        Tag identifiers to filter the search

    search: str, optional
        Search term to filter results (default is empty string)

    user: str, optional
        Username to filter the search to specific user's datasets

    mine: bool, optional
        If True, returns only the user's personal datasets (default is False)

    page: int, optional
        The page number to return (default is 1)

    max_size: int, optional
        Maximum size in bytes to filter datasets by

    min_size: int, optional
        Minimum size in bytes to filter datasets by

    size: Deprecated
        This parameter is deprecated and should not be used

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "datasets": list (only if success)
        }
    """
    try:
        loop = asyncio.get_running_loop()
        datasets = await loop.run_in_executor(
            None,
            lambda: api.dataset_list(
                sort_by=sort_by, size=size, file_type=file_type,
                license_name=license_name, tag_ids=tag_ids, search=search,
                user=user, mine=mine, page=page, max_size=max_size, min_size=min_size
            )
        )
        return {
            "status": "success",
            "message": f"Retrieved {len(datasets)} datasets.",
            "datasets": datasets,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def dataset_metadata(dataset: str, path: str = None) -> dict:
    """Download the metadata file for a dataset.

    Parameters
    ----------
    dataset : str
        Dataset URL suffix in format <owner>/<dataset-name>
    path : str, optional
        Local directory path where metadata will be saved (default: current working directory)

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str
        }
    """
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: api.dataset_metadata(dataset, path=path))
        return {
            "status": "success",
            "message": f"Downloaded metadata for dataset: {dataset} to path: {path or os.getcwd()}",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def dataset_list_files(dataset: str, page_token: str = None, page_size: int = 20) -> dict:
    """Retrieve a list of all files contained within a specific Kaggle dataset.

    Parameters
    ----------
    dataset : str
        The unique identifier of the dataset in the format 'owner/dataset-name'
        Example: 'netflix/netflix-prize-data'
    page_token : str, optional
        Token for paginating through results when there are multiple pages (default: None)
    page_size : int, optional
        Number of files to return per page (default: 20, range: 1–100)

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "files": list (only if success)
        }
    """
    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: api.dataset_list_files(dataset, page_token=page_token, page_size=page_size)
        )
        return {
            "status": "success",
            "message": f"Retrieved {len(response.files)} files for dataset: {dataset}",
            "files": [f for f in response.files],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def dataset_status(dataset: str) -> dict:
    """Get the status of a dataset. Only for your own datasets.

    Parameters
    ----------
    dataset : str
        Dataset URL suffix in format <owner>/<dataset-name> 
        (use "kaggle datasets list" to show options)

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "dataset_status": dict (only if success)
        }
    """
    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: api.dataset_status(dataset))
        return {
            "status": "success",
            "message": f"Retrieved status for dataset: {dataset}",
            "dataset_status": response,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def dataset_download_file(dataset: str, file_name: str, path: str = None, force=False, quiet=True, licenses=[]) -> dict:
    """Download a specific file from a Kaggle dataset to a local directory.

    Parameters
    ----------
    dataset: str
        The unique identifier of the dataset in the format 'owner/dataset-name'

    file_name: str
        The name of the file to download from the dataset

    path: str, optional
        The local directory path where the file should be saved
        If not specified, downloads to the current working directory

    force: bool, optional
        Whether to overwrite the file if it already exists locally
        Default: False

    quiet: bool, optional
        Whether to suppress download progress and status messages
        Default: True

    licenses: list[str], optional
        List of specific dataset license names to accept. Valid values:
        - 'all': Accept all license types
        - 'cc': Accept Creative Commons licenses
        - 'gpl': Accept GPL (GNU General Public License)
        - 'odb': Accept Open Database licenses
        - 'other': Accept other license types
        Default: [] (empty list accepts all licenses)

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str
        }

    Notes
    -----
    The dataset must be publicly accessible or you must have permission to access it.
    Some datasets may require accepting specific licenses before downloading.
    """
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: api.dataset_download_file(
                dataset, file_name, path=path, force=force, quiet=quiet, licenses=licenses
            ),
        )
        return {
            "status": "success",
            "message": f"Downloaded {file_name} from dataset: {dataset} to path: {path or os.getcwd()}",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def dataset_download_files(dataset: str, path: str = None, force: bool = False, quiet: bool = True, licenses: list = None) -> dict:
    """Download all files from a Kaggle dataset to a local directory.

    Parameters
    ----------
    dataset: str
        The unique identifier of the dataset in the format 'owner/dataset-name'
        Example: 'netflix/netflix-prize-data' or 'google/covid-19-open-data'

    path: str, optional
        Local directory path where dataset files will be saved
        If not specified, downloads to current working directory
        
    force: bool, optional
        Whether to overwrite files if they already exist locally
        Default: False
        
    quiet: bool, optional
        Whether to suppress download progress messages
        Default: True

    licenses: list[str], optional
        List of specific dataset license names to accept. Valid values:
        - 'all': Accept all license types
        - 'cc': Accept Creative Commons licenses
        - 'gpl': Accept GPL (GNU General Public License)
        - 'odb': Accept Open Database licenses
        - 'other': Accept other license types
        Default: [] (empty list accepts all licenses)

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": <confirmation or error message>
        }

    Notes
    -----
    The dataset must be publicly accessible or you must have permission to access it.
    Some datasets may require accepting specific licenses before downloading.
    """
    try:
        api.dataset_download_files(dataset, path=path, force=force, quiet=quiet, licenses=licenses)
        return {
            "status": "success",
            "message": f"Downloaded dataset: {dataset} to path: {path or os.getcwd()}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool()
def dataset_create(folder: str, public: bool = False, quiet: bool = False, convert_to_csv: bool = True, dir_mode: str = 'skip') -> dict:
    """Create a new Kaggle dataset from a local folder with metadata configuration.

    Parameters
    ----------
    folder: str
        Path to the folder containing the dataset files and metadata.json

    public: bool, optional
        Whether to make the dataset publicly accessible
        Default: False

    quiet: bool, optional
        Whether to suppress progress and status messages
        Default: False

    convert_to_csv: bool, optional
        Whether to automatically convert compatible files to CSV format
        Default: True

    dir_mode: str, optional
        How to handle directories in the dataset:
        - 'skip': Ignore directories (default)
        - 'zip': Compress directories and upload as zip files
        Default: 'skip'

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": dict (API response)
        }
    """
    import os

    if not folder or not os.path.isdir(folder):
        return {"status": "error", "message": f"Folder does not exist: {folder}"}

    try:
        response = api.dataset_create_new(
            folder,
            public=public,
            quiet=quiet,
            convert_to_csv=convert_to_csv,
            dir_mode=dir_mode
        )

        if hasattr(response, "to_dict"):
            response_dict = response.to_dict()
        else:
            response_dict = response.__dict__

        if response_dict.get("error", "") == "":
            response_dict["message"] = f"Dataset created successfully from folder: {folder}"
            return {
                "status": "success",
                "message": response_dict["message"],
                "data": response_dict
            }
        else:
            return {
                "status": "error",
                "message": response_dict.get("error", "Unknown error occurred."),
                "data": response_dict
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
def dataset_initialize(folder: str) -> dict:
    """Initialize a new Kaggle dataset in a local folder with metadata configuration.

    Parameters
    ----------
    folder: str
        Path to the folder where dataset files and metadata.json are located or will be created.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": <confirmation or error message>
        }
    """
    import os

    # Validate folder existence
    if not folder or not os.path.isdir(folder):
        return {"status": "error", "message": f"Folder does not exist: {folder}"}

    try:
        api.dataset_initialize(folder)
        return {"status": "success", "message": f"Initialized dataset in folder: {folder}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
async def dataset_create_version(folder: str, version_notes: str, quiet: bool = False, convert_to_csv: bool = True, delete_old_versions: bool = False,dir_mode: str = 'skip') -> dict:
    """Create a new version of an existing Kaggle dataset.

    Parameters
    ----------
    folder: str
        Path to the folder containing dataset files and configuration

    version_notes: str
        Description of changes in this version

    quiet: bool, optional
        Whether to suppress progress and status messages
        Default: False

    convert_to_csv: bool, optional
        Whether to automatically convert compatible files to CSV format
        Default: True

    delete_old_versions: bool, optional
        Whether to remove previous versions of this dataset
        Default: False

    dir_mode: str, optional
        How to handle directories in the dataset:
        - 'skip': Ignore directories (default)
        - 'zip': Compress directories and upload as zip files
        Default: 'skip'

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": dict (API response)
        }
    """
    import os

    if not folder or not os.path.isdir(folder):
        return {"status": "error", "message": f"Folder does not exist: {folder}"}

    try:
        response = api.dataset_create_version(
            folder,
            version_notes,
            quiet=quiet,
            convert_to_csv=convert_to_csv,
            delete_old_versions=delete_old_versions,
            dir_mode=dir_mode
        )

        if hasattr(response, "to_dict"):
            response_dict = response.to_dict()
        else:
            response_dict = response.__dict__

        if response_dict.get("error", "") == "":
            response_dict["message"] = f"New version created successfully for dataset in folder: {folder}"
            return {
                "status": "success",
                "message": response_dict["message"],
                "data": response_dict
            }
        else:
            return {
                "status": "error",
                "message": response_dict.get("error", "Unknown error occurred."),
                "data": response_dict
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}


#-----------
# Kernels
#-----------

@mcp.tool()
async def kernels_list(page_size: int = 20, page: int = 1, search: str = None, competition: str = None, dataset: str = None, user: str = None, mine: bool = False, sort_by: str = None, language: str = None, kernel_type: str = None, output_type: str = None ) -> dict:
    """Search and list Kaggle kernels based on specified criteria.

    Parameters
    ----------
    page: int, optional
        Page number of results to return. Default: 1

    page_size: int, optional
        Number of results per page. Default: 20

    search: str, optional
        Custom search query string.

    competition: str, optional
        Filter kernels to a specific competition.

    dataset: str, optional
        Filter kernels to a specific dataset in format 'owner/dataset-name'.

    user: str, optional
        Filter kernels to a specific username.

    mine: bool, optional
        If True, show only your own kernels. Default: False

    language: str, optional
        Filter by programming language. Valid: 'all', 'python', 'r', 'sqlite', 'julia'.

    kernel_type: str, optional
        Type of kernel to return. Valid: 'all', 'script', 'notebook'.

    output_type: str, optional
        Filter by kernel output type. Valid: 'all', 'visualization', 'data'.

    sort_by: str, optional
        Sort results criteria. Valid: 'hotness', 'commentCount', 'dateCreated', 
        'dateRun', 'relevance', 'scoreAscending', 'scoreDescending', 'viewCount', 'voteCount'.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": list of kernel metadata (if successful)
        }
    """
    try:
        loop = asyncio.get_running_loop()
       
        kernels = await loop.run_in_executor(
            None,
            lambda: api.kernels_list(
                page_size=page_size,
                page=page,
                search=search,
                competition=competition,
                dataset=dataset,
                user=user,
                mine=mine,
                sort_by=sort_by,
                language=language,
                kernel_type=kernel_type,
                output_type=output_type
            )
        )

        kernels_data = [kernel.to_dict() if hasattr(kernel, "to_dict") else kernel.__dict__ for kernel in kernels]

        return {
            "status": "success",
            "message": f"Retrieved {len(kernels_data)} kernels.",
            "data": kernels_data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list kernels: {str(e)}",
            "data": []
        }



@mcp.tool()
async def kernel_list_files(kernel: str, page_token: str = None, page_size: int = 20) -> dict:
    """List files associated with a specific Kaggle kernel.

    Parameters
    ----------
    kernel: str
        Kernel identifier in format 'owner/kernel-name'.
        Example: 'username/my-analysis'.
    page_token: str, optional
        Token for pagination through results. Default: None
    page_size: int, optional
        Number of files to return per page. Default: 20

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": list of file metadata (if successful)
        }
    """
    import re

    if not kernel or not re.match(r'^[^/]+/[^/]+$', kernel):
        return {"status": "error", "message": f"Invalid kernel format: {kernel}", "data": []}

    try:
        loop = asyncio.get_running_loop()
        files_response = await loop.run_in_executor(
            None,
            lambda: api.kernels_list_files(kernel, page_token=page_token, page_size=page_size)
        )

        files_data = [f.to_dict() if hasattr(f, "to_dict") else f.__dict__ for f in getattr(files_response, "files", [])]

        return {
            "status": "success",
            "message": f"Retrieved {len(files_data)} files from kernel: {kernel}",
            "data": files_response
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list files for kernel {kernel}: {str(e)}",
            "data": []
        }



@mcp.tool()
async def kernel_initialize(folder: str) -> dict:
    """Initialize kernel metadata configuration in a specified folder.

    Parameters
    ----------
    folder: str
        Path to the directory where kernel metadata will be created.
        Creates kernel-metadata.json with default configuration values.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": dict (optional, typically empty)
        }
    """

    if not folder or not os.path.isdir(folder):
        return {"status": "error", "message": f"Folder does not exist: {folder}", "data": {}}

    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: api.kernels_initialize(folder))

        return {
            "status": "success",
            "message": f"Initialized kernel metadata in folder: {folder}",
            "data": {}
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize kernel metadata: {str(e)}",
            "data": {}
        }



@mcp.tool()
async def kernel_push(folder: str, timeout: int = None) -> dict:
    """
    Push a Kaggle kernel and its metadata from a local folder.

    This tool validates the specified kernel directory, ensures the required
    metadata file exists, and then pushes the kernel to Kaggle using the Kaggle API.
    It returns structured status information instead of raising exceptions,
    allowing LLMs or external systems to interpret results programmatically.

    Parameters
    ----------
    folder : str
        Path to the directory containing:
        - kernel-metadata.json
        - Kernel notebook or script files.

    timeout : int, optional
        Maximum execution time in seconds. Default is None (no timeout).

    Returns
    -------
    dict
        On success:
        {
            "status": "success",
            "ref": str,                # Kernel reference path
            "url": str,                # Full URL to the pushed kernel on Kaggle
            "versionNumber": int,      # Version number of the pushed kernel
            ...                        # Any additional fields from the Kaggle API
        }

        On error:
        {
            "status": "error",
            "message": str,             # Description of the failure
            ...                         # Optional additional info
        }
    """

    if not folder or not os.path.isdir(folder):
        return {"status": "error", "message": f"Folder path does not exist: {folder}"}

    metadata_path = os.path.join(folder, "kernel-metadata.json")
    if not os.path.exists(metadata_path):
        return {"status": "error", "message": f"kernel-metadata.json not found in {folder}"}

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: api.kernels_push(folder, timeout=timeout)
        )

        # Convert response to dict
        response_dict = (
            response.to_dict() if hasattr(response, "to_dict")
            else dict(response) if isinstance(response, dict)
            else response.__dict__
        )

        # Check for API-reported errors
        if response_dict.get("error"):
            return {"status": "error", "message": response_dict["error"], **response_dict}

        # Check for invalid fields such as invalid tags/sources
        invalid_fields = {k: v for k, v in response_dict.items() if k.startswith("invalid") and v}
        if invalid_fields:
            return {
                "status": "error",
                "message": "Validation errors occurred",
                **response_dict,
            }

        return {"status": "success", **response_dict}

    except Exception as e:
        return {"status": "error", "message": f"Failed to push kernel: {str(e)}"}




@mcp.tool()
async def kernel_pull(kernel: str, path: str, metadata: bool = False, quiet: bool = True) -> dict:
    """
    Download a Kaggle kernel and its files to a local directory.

    Parameters
    ----------
    kernel : str
        Kernel identifier in format 'owner/kernel-name'.

    path : str
        Local directory path where kernel files will be downloaded.

    metadata : bool, optional
        Whether to download kernel-metadata.json file.
        Default: False

    quiet : bool, optional
        Whether to suppress progress messages.
        Default: True

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "kernel": str,
            "saved_path": str (only if success)
        }
    """

    if not kernel or '/' not in kernel:
        return {
            "status": "error",
            "message": "Kernel must be specified in the form 'username/kernel-slug'.",
            "kernel": kernel,
        }

    try:
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

        loop = asyncio.get_running_loop()
        pulled_file = await loop.run_in_executor(
            None,
            lambda: api.kernels_pull(kernel, path, metadata=metadata, quiet=quiet)
        )

        abs_path = os.path.abspath(os.path.join(path, pulled_file))
        if not os.path.exists(abs_path):
            return {
                "status": "error",
                "message": f"Kernel pulled but expected file not found at {abs_path}.",
                "kernel": kernel,
            }

        return {
            "status": "success",
            "message": f"Kernel '{kernel}' downloaded successfully.",
            "kernel": kernel,
            "saved_path": abs_path,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error while downloading kernel '{kernel}': {str(e)}",
            "kernel": kernel,
        }




@mcp.tool()
async def kernel_output(kernel: str, path: str, force: bool = False, quiet: bool = True) -> dict:
    """
    Download the execution output files from a Kaggle kernel.

    Parameters
    ----------
    kernel: str
        Kernel identifier in format 'owner/kernel-name'.

    path: str
        Local directory path where output files will be saved.

    force: bool, optional
        Whether to overwrite existing output files. Default: False.

    quiet: bool, optional
        Whether to suppress progress messages. Default: True.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "kernel": str,
            "saved_path": str (only if success)
        }
    """

    if not kernel or '/' not in kernel:
        return {
            "status": "error",
            "message": "Kernel must be specified in the form 'username/kernel-slug'.",
            "kernel": kernel,
        }

    try:
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

        loop = asyncio.get_running_loop()
        saved_path = await loop.run_in_executor(
            None,
            lambda: api.kernels_output(kernel, path, force=force, quiet=quiet)
        )

        abs_path = os.path.abspath(path)
        return {
            "status": "success",
            "message": f"Downloaded output for kernel '{kernel}' to path: {abs_path}",
            "kernel": kernel,
            "saved_path": abs_path,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to download output for kernel '{kernel}': {str(e)}",
            "kernel": kernel,
        }



@mcp.tool()
async def kernel_status(kernel: str) -> dict:
    """
    Get the status of a Kaggle kernel.

    Parameters
    ----------
    kernel: str
        Kernel identifier in format 'owner/kernel-name'.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "kernel": str,
            "data": dict (kernel status info, if success)
        }
    """
    if not kernel or '/' not in kernel:
        return {
            "status": "error",
            "message": "Kernel must be specified in the form 'username/kernel-slug'.",
            "kernel": kernel,
            "data": {}
        }

    try:
        loop = asyncio.get_running_loop()
        status_response = await loop.run_in_executor(None, lambda: api.kernels_status(kernel))

        status_data = (
            status_response.to_dict() if hasattr(status_response, "to_dict")
            else dict(status_response) if isinstance(status_response, dict)
            else getattr(status_response, "__dict__", {})
        )

        return {
            "status": "success",
            "message": f"Retrieved status for kernel '{kernel}'.",
            "kernel": kernel,
            "data": status_data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve kernel status for '{kernel}': {str(e)}",
            "kernel": kernel,
            "data": {}
        }



#-----------
# Models
#-----------


@mcp.tool()
async def models_list(sort_by: str = None, search: str = None, owner: str = None, page_size: int = 20, page_token: str = None) -> dict:
    """
    Search and list Kaggle models based on specified criteria.

    Parameters
    ----------
    sort_by: str, optional
        Sort results criteria. Valid options:
        - 'hotness': trending/popularity
        - 'downloadCount': number of downloads
        - 'voteCount': number of votes
        - 'notebookCount': number of notebooks
        - 'createTime': creation date

    search: str, optional
        Search term to filter results. Default: None

    owner: str, optional
        Username or organization to filter models by.

    page_size: int, optional
        Number of results per page. Default: 20

    page_token: str, optional
        Token for pagination through results. Default: None

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": list of model metadata (if successful)
        }
    """
    try:
        loop = asyncio.get_running_loop()
        models_response = await loop.run_in_executor(
            None,
            lambda: api.model_list(
                sort_by=sort_by,
                search=search,
                owner=owner,
                page_size=page_size,
                page_token=page_token
            )
        )

        models_data = [
            m.to_dict() if hasattr(m, "to_dict") else m.__dict__ for m in models_response
        ]

        return {
            "status": "success",
            "message": f"Retrieved {len(models_data)} models.",
            "data": models_data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list models: {str(e)}",
            "data": []
        }



@mcp.tool()
async def model_get(model: str, path: str = None) -> dict:
    """
    Retrieve metadata and details for a specific Kaggle model, and save it as a JSON file.

    Parameters
    ----------
    model: str
        Model identifier in format 'owner/model-name'.
        Example: 'google/bert' or 'username/custom-model'.

    path: str, optional
        Directory path where the JSON file ('model-metadata.json') will be saved.
        Default: current working directory.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "model": str,
            "data": dict (model metadata if success),
            "file_path": str (path to saved JSON file if success)
        }

    Side Effects
    ------------
    Creates 'model-metadata.json' at the specified path containing the API response.
    """
    import json

    if not model or '/' not in model:
        return {
            "status": "error",
            "message": "Model must be specified in the form 'owner/model-slug'.",
            "model": model,
            "data": {},
            "file_path": ""
        }

    if path is None:
        path = os.getcwd()

    try:
        os.makedirs(path, exist_ok=True)

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: api.model_get(model))

        response_dict = (
            response.to_dict() if hasattr(response, "to_dict")
            else response.__dict__
        )

        file_path = os.path.join(path, "model-metadata.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(response_dict, f, indent=4, ensure_ascii=False)

        return {
            "status": "success",
            "message": f"Model '{model}' metadata retrieved and saved successfully.",
            "model": model,
            "data": response_dict,
            "file_path": os.path.abspath(file_path)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve model '{model}': {str(e)}",
            "model": model,
            "data": {},
            "file_path": ""
        }



@mcp.tool()
async def model_initialize(folder: str) -> dict:
    """
    Initialize model metadata configuration in a specified folder.

    Parameters
    ----------
    folder: str
        Path to the directory where model metadata will be created.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": dict (optional, typically empty)
        }

    Side Effects
    ------------
    Creates the model-metadata.json file with default configuration in the specified directory.
    """
    try:
        os.makedirs(folder, exist_ok=True)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: api.model_initialize(folder))

        return {
            "status": "success",
            "message": f"Initialized model metadata in folder: {folder}",
            "data": {}
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize model metadata: {str(e)}",
            "data": {}
        }


@mcp.tool()
async def model_create(folder: str) -> dict:
    """
    Create a new model on Kaggle using metadata from a local folder.

    Parameters
    ----------
    folder : str
        Absolute path to the folder containing model-metadata.json and model assets.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": dict (API response with model id, ref, url, etc.)
        }
    """
    import asyncio
    import os

    if not folder or not os.path.isdir(folder):
        return {"status": "error", "message": f"Folder does not exist: {folder}", "data": {}}

    metadata_path = os.path.join(folder, "model-metadata.json")
    if not os.path.exists(metadata_path):
        return {"status": "error", "message": f"model-metadata.json not found in {folder}", "data": {}}

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: api.model_create_new(folder))

        response_dict = (
            response.to_dict() if hasattr(response, "to_dict")
            else dict(response) if isinstance(response, dict)
            else response.__dict__
        )

        if response_dict.get("error"):
            return {"status": "error", "message": response_dict["error"], "data": response_dict}

        response_dict["message"] = "Model created successfully."
        return {"status": "success", "message": response_dict["message"], "data": response_dict}

    except Exception as e:
        return {"status": "error", "message": f"Failed to create model: {str(e)}", "data": {}}



@mcp.tool()
async def model_update(folder: str) -> dict:
    """
    Update an existing model on Kaggle using metadata from a local folder.

    Parameters
    ----------
    folder : str
        Absolute path to the folder containing model-metadata.json and model assets.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": dict (API response with model id, ref, url, etc.)
        }
    """

    if not folder or not os.path.isdir(folder):
        return {"status": "error", "message": f"Folder does not exist: {folder}", "data": {}}

    metadata_path = os.path.join(folder, "model-metadata.json")
    if not os.path.exists(metadata_path):
        return {"status": "error", "message": f"model-metadata.json not found in {folder}", "data": {}}

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: api.model_update(folder))

        response_dict = (
            response.to_dict() if hasattr(response, "to_dict")
            else dict(response) if isinstance(response, dict)
            else response.__dict__
        )

        if response_dict.get("error"):
            return {"status": "error", "message": response_dict["error"], "data": response_dict}

        response_dict["message"] = "Model updated successfully."
        return {"status": "success", "message": response_dict["message"], "data": response_dict}

    except Exception as e:
        return {"status": "error", "message": f"Failed to update model: {str(e)}", "data": {}}




@mcp.tool()
async def model_delete(model: str, confirmation: bool) -> dict:
    """
    Delete a model from Kaggle.

    Parameters
    ----------
    model: str
        Model identifier in format 'owner/model-name'.

    confirmation: bool
        Must be True to confirm deletion.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "model": str,
            "data": dict (API response if available)
        }
    """
    import asyncio

    if not model or '/' not in model:
        return {"status": "error", "message": "Model must be specified as 'owner/model-name'.", "model": model, "data": {}}

    if not confirmation:
        return {"status": "error", "message": "Deletion not confirmed. Set confirmation=True to delete.", "model": model, "data": {}}

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: api.model_delete(model, yes=confirmation))

        response_dict = (
            response.to_dict() if hasattr(response, "to_dict")
            else dict(response) if isinstance(response, dict)
            else response.__dict__
        )

        if response_dict.get("error"):
            return {"status": "error", "message": response_dict["error"], "model": model, "data": response_dict}

        return {"status": "success", "message": f"Model '{model}' deleted successfully.", "model": model, "data": response_dict}

    except Exception as e:
        return {"status": "error", "message": f"Failed to delete model '{model}': {str(e)}", "model": model, "data": {}}



@mcp.tool()
async def model_instance_get(model_instance: str, path: str = None) -> dict:
    """
    Retrieve details of a specific model instance from Kaggle and save as JSON.

    Parameters
    ----------
    model_instance: str
        Model instance identifier in format 'owner/model-name/framework/instance-slug'.

    path: str, optional
        Directory path where 'model-instance-metadata.json' will be saved.
        Default: current working directory.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "model_instance": str,
            "data": dict (metadata if success),
            "file_path": str (path to saved JSON if success)
        }

    Side Effects
    ------------
    Creates 'model-instance-metadata.json' at the specified path containing the API response.
    """
    if not model_instance or '/' not in model_instance:
        return {
            "status": "error",
            "message": "Model instance must be specified in the form 'owner/model/framework/instance-slug'.",
            "model_instance": model_instance,
            "data": {},
            "file_path": ""
        }

    if path is None:
        path = os.getcwd()

    try:
        os.makedirs(path, exist_ok=True)

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: api.model_instance_get(model_instance))

        response_dict = response.to_dict() if hasattr(response, "to_dict") else response.__dict__

        file_path = os.path.join(path, "model-instance-metadata.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(response_dict, f, indent=4, ensure_ascii=False)

        return {
            "status": "success",
            "message": f"Model instance '{model_instance}' retrieved and saved successfully.",
            "model_instance": model_instance,
            "data": response_dict,
            "file_path": os.path.abspath(file_path)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve model instance '{model_instance}': {str(e)}",
            "model_instance": model_instance,
            "data": {},
            "file_path": ""
        }


@mcp.tool()
async def model_instance_initialize(folder: str) -> dict:
    """
    Initialize model instance metadata configuration in a specified folder.

    Parameters
    ----------
    folder: str
        Path to the directory where model instance metadata will be created.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": dict (optional, typically empty)
        }

    Side Effects
    ------------
    Creates the model instance metadata file with default configuration in the specified directory.
    """
    import asyncio
    import os

    try:
        os.makedirs(folder, exist_ok=True)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: api.model_instance_initialize(folder))

        return {
            "status": "success",
            "message": f"Initialized model instance metadata in folder: {folder}",
            "data": {}
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize model instance metadata: {str(e)}",
            "data": {}
        }


@mcp.tool()
async def model_instance_create(folder: str, quiet: bool = False, dir_mode: str = 'skip') -> dict:
    """
    Create a new model instance on Kaggle using metadata from a local folder.

    Parameters
    ----------
    folder : str
        Path to the folder containing model-instance-metadata.json and model assets.

    quiet: bool, optional
        Whether to suppress progress and status messages. Default: False

    dir_mode: str, optional
        How to handle directories in the model instance:
        - 'skip': Ignore directories (default)
        - 'zip': Compress directories and upload as zip files
        Default: 'skip'

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": dict (API response with id, ref, url, etc.)
        }
    """
    if not folder or not os.path.isdir(folder):
        return {"status": "error", "message": f"Folder does not exist: {folder}", "data": {}}

    metadata_path = os.path.join(folder, "model-instance-metadata.json")
    if not os.path.exists(metadata_path):
        return {"status": "error", "message": f"model-instance-metadata.json not found in {folder}", "data": {}}

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, lambda: api.model_instance_create(folder, quiet=quiet, dir_mode=dir_mode)
        )

        response_dict = (
            response.to_dict() if hasattr(response, "to_dict")
            else dict(response) if isinstance(response, dict)
            else response.__dict__
        )

        if response_dict.get("error"):
            return {"status": "error", "message": response_dict["error"], "data": response_dict}

        response_dict["message"] = "Model instance created successfully."
        return {"status": "success", "message": response_dict["message"], "data": response_dict}

    except Exception as e:
        return {"status": "error", "message": f"Failed to create model instance: {str(e)}", "data": {}}

    
    
@mcp.tool()
async def model_instance_update(folder: str) -> dict:
    """
    Update an existing model instance using metadata from a local folder.

    Parameters
    ----------
    folder: str
        Path to the folder containing model-instance-metadata.json and updated assets.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "data": dict (API response with id, ref, url, etc.)
        }
    """
    if not folder or not os.path.isdir(folder):
        return {"status": "error", "message": f"Folder does not exist: {folder}", "data": {}}

    metadata_path = os.path.join(folder, "model-instance-metadata.json")
    if not os.path.exists(metadata_path):
        return {"status": "error", "message": f"model-instance-metadata.json not found in {folder}", "data": {}}

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: api.model_instance_update(folder))

        response_dict = (
            response.to_dict() if hasattr(response, "to_dict")
            else dict(response) if isinstance(response, dict)
            else response.__dict__
        )

        if response_dict.get("error"):
            return {"status": "error", "message": response_dict["error"], "data": response_dict}

        response_dict["message"] = "Model instance updated successfully."
        return {"status": "success", "message": response_dict["message"], "data": response_dict}

    except Exception as e:
        return {"status": "error", "message": f"Failed to update model instance: {str(e)}", "data": {}}



@mcp.tool()
async def model_instance_delete(model_instance: str, confirmation: bool) -> dict:
    """
    Delete a model instance from Kaggle.

    Parameters
    ----------
    model_instance: str
        Model instance identifier in format 'owner/model-name/framework/instance-slug'.

    confirmation: bool
        Must be True to confirm deletion.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "model_instance": str,
            "data": dict (API response if available)
        }
    """
    import asyncio

    if not model_instance or '/' not in model_instance:
        return {
            "status": "error",
            "message": "Model instance must be specified as 'owner/model/framework/instance-slug'.",
            "model_instance": model_instance,
            "data": {}
        }

    if not confirmation:
        return {
            "status": "error",
            "message": "Deletion not confirmed. Set confirmation=True to delete.",
            "model_instance": model_instance,
            "data": {}
        }

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, lambda: api.model_instance_delete(model_instance, yes=confirmation)
        )

        response_dict = (
            response.to_dict() if hasattr(response, "to_dict")
            else dict(response) if isinstance(response, dict)
            else response.__dict__
        )

        if response_dict.get("error"):
            return {"status": "error", "message": response_dict["error"], "model_instance": model_instance, "data": response_dict}

        return {"status": "success", "message": f"Model instance '{model_instance}' deleted successfully.", "model_instance": model_instance, "data": response_dict}

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete model instance '{model_instance}': {str(e)}",
            "model_instance": model_instance,
            "data": {}
        }



@mcp.tool()
async def model_instance_version_create(model_instance: str, folder: str, version_notes: str = '', quiet: bool = False, dir_mode: str = 'skip') -> dict:
    """
    Create a new version of an existing model instance.

    Parameters
    ----------
    model_instance: str
        Model instance identifier in format 'owner/model-name/framework/instance-slug'.

    folder: str
        Path to folder containing model instance files and metadata.

    version_notes: str, optional
        Description of changes in this version. Default: ''.

    quiet: bool, optional
        Whether to suppress progress messages. Default: False.

    dir_mode: str, optional
        How to handle directories:
        - 'skip': Ignore directories (default)
        - 'zip': Compress and upload as zip files. Default: 'skip'.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "model_instance": str,
            "data": dict (API response with version details)
        }
    """
    if not model_instance or '/' not in model_instance:
        return {
            "status": "error",
            "message": "Model instance must be specified as 'owner/model/framework/instance-slug'.",
            "model_instance": model_instance,
            "data": {}
        }

    if not folder or not os.path.isdir(folder):
        return {"status": "error", "message": f"Folder does not exist: {folder}", "model_instance": model_instance, "data": {}}

    metadata_path = os.path.join(folder, "model-instance-metadata.json")
    if not os.path.exists(metadata_path):
        return {"status": "error", "message": f"model-instance-metadata.json not found in {folder}", "model_instance": model_instance, "data": {}}

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: api.model_instance_version_create(
                model_instance,
                folder,
                version_notes=version_notes,
                quiet=quiet,
                dir_mode=dir_mode
            )
        )

        response_dict = (
            response.to_dict() if hasattr(response, "to_dict")
            else dict(response) if isinstance(response, dict)
            else response.__dict__
        )

        if response_dict.get("error"):
            return {"status": "error", "message": response_dict["error"], "model_instance": model_instance, "data": response_dict}

        response_dict["message"] = "Model instance version created successfully."
        return {"status": "success", "message": response_dict["message"], "model_instance": model_instance, "data": response_dict}

    except Exception as e:
        return {"status": "error", "message": f"Failed to create model instance version: {str(e)}", "model_instance": model_instance, "data": {}}



@mcp.tool()
async def model_instance_version_download(model_instance_version: str, path: str = None, force: bool = False, quiet: bool = True, untar: bool = False) -> dict:
    """
    Download all files for a model instance version to a local directory.

    Parameters
    ----------
    model_instance_version: str
        Model instance version identifier in format 'owner/model-name/framework/instance-slug/version-number'.

    path: str, optional
        Local directory path where version files will be downloaded.
        If not specified, downloads to current working directory.

    force: bool, optional
        Whether to overwrite files if they already exist locally. Default: False.

    quiet: bool, optional
        Whether to suppress progress and status messages. Default: True.

    untar: bool, optional
        Whether to automatically extract downloaded tar archives. Default: False.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "model_instance_version": str,
            "saved_path": str (absolute path to download location)
        }
    """
    if not model_instance_version or '/' not in model_instance_version:
        return {
            "status": "error",
            "message": "Model instance version must be specified as 'owner/model/framework/instance-slug/version-number'.",
            "model_instance_version": model_instance_version,
            "saved_path": ""
        }

    if path is None:
        path = os.getcwd()
    try:
        os.makedirs(path, exist_ok=True)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: api.model_instance_version_download(
                model_instance_version,
                path=path,
                force=force,
                quiet=quiet,
                untar=untar
            )
        )

        abs_path = os.path.abspath(path)
        return {
            "status": "success",
            "message": f"Downloaded model instance version '{model_instance_version}' successfully.",
            "model_instance_version": model_instance_version,
            "saved_path": abs_path
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to download model instance version '{model_instance_version}': {str(e)}",
            "model_instance_version": model_instance_version,
            "saved_path": ""
        }



@mcp.tool()
async def model_instance_version_files(
    model_instance_version: str,
    page_token: str = None,
    page_size: int = 20,
    csv_display: bool = False
) -> dict:
    """
    List all files contained in a specific model instance version.

    Parameters
    ----------
    model_instance_version: str
        Model instance version identifier in format 'owner/model-name/framework/instance-slug/version-number'.

    page_token: str, optional
        Token for paginating through results when there are multiple pages. Default: None.

    page_size: int, optional
        Number of files to return per page. Default: 20.

    csv_display: bool, optional
        Whether to format output as comma-separated values instead of table format. Default: False.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "model_instance_version": str,
            "files": list of dicts with keys: name, size, creationDate
        }
    """
    if not model_instance_version or '/' not in model_instance_version:
        return {
            "status": "error",
            "message": "Model instance version must be specified as 'owner/model/framework/instance-slug/version-number'.",
            "model_instance_version": model_instance_version,
            "files": []
        }

    try:
        loop = asyncio.get_running_loop()
        api_response = await loop.run_in_executor(
            None,
            lambda: api.model_instance_version_files(
                model_instance_version,
                page_token=page_token,
                page_size=page_size,
                csv_display=csv_display
            )
        )

        files_list = [f for f in getattr(api_response, "files", [])]

        return {
            "status": "success",
            "message": f"Retrieved {len(files_list)} files for model instance version '{model_instance_version}'.",
            "model_instance_version": model_instance_version,
            "files": files_list
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve files for model instance version '{model_instance_version}': {str(e)}",
            "model_instance_version": model_instance_version,
            "files": []
        }



@mcp.tool()
async def model_instance_version_delete(model_instance_version: str, confirmation: bool) -> dict:
    """
    Delete a specific version of a model instance from Kaggle.

    Parameters
    ----------
    model_instance_version: str
        Model instance version identifier in format 'owner/model-name/framework/instance-slug/version-number'.

    confirmation: bool
        Must be True to confirm deletion.

    Returns
    -------
    dict
        {
            "status": "success" | "error",
            "message": str,
            "model_instance_version": str,
            "data": dict (API response if available)
        }
    """
    import asyncio

    if not model_instance_version or '/' not in model_instance_version:
        return {
            "status": "error",
            "message": "Model instance version must be specified as 'owner/model/framework/instance-slug/version-number'.",
            "model_instance_version": model_instance_version,
            "data": {}
        }

    if not confirmation:
        return {
            "status": "error",
            "message": "Deletion not confirmed. Set confirmation=True to delete.",
            "model_instance_version": model_instance_version,
            "data": {}
        }

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, lambda: api.model_instance_version_delete(model_instance_version, yes=confirmation)
        )

        response_dict = (
            response.to_dict() if hasattr(response, "to_dict")
            else dict(response) if isinstance(response, dict)
            else response.__dict__
        )

        if response_dict.get("error"):
            return {
                "status": "error",
                "message": response_dict["error"],
                "model_instance_version": model_instance_version,
                "data": response_dict
            }

        return {
            "status": "success",
            "message": f"Model instance version '{model_instance_version}' deleted successfully.",
            "model_instance_version": model_instance_version,
            "data": response_dict
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete model instance version '{model_instance_version}': {str(e)}",
            "model_instance_version": model_instance_version,
            "data": {}
        }



def main():
    """Main entry point for the Kaggle MCP server."""
    print("MCP server started successfully")
    mcp.run(transport='stdio')

    
if __name__ == "__main__":
    init_kaggle()
    from kaggle import api
    main()
    
