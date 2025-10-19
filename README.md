# Kaggle MCP Server

A Model Context Protocol (MCP) server that provides seamless integration with the Kaggle API. Interact with Kaggle competitions, datasets, kernels, and models through MCP-compatible clients like Claude Desktop.

##  Features

-  **Competitions**: List, download files, submit, view leaderboards and submissions
-  **Datasets**: Search, download, create, and manage datasets with version control
-  **Kernels**: List, push, pull, and manage Kaggle notebooks and scripts
-  **Models**: Create, update, and manage ML models and instances with full version control

##  Installation

### Prerequisites

- Python 3.10 or higher
- A Kaggle account with API credentials


### Install from Source

```bash
git clone https://github.com/Seif-Sameh/kaggle-mcp.git
cd kaggle-mcp
```

## Setup

### 1. Get Your Kaggle API Credentials

1. Go to [https://www.kaggle.com/account](https://www.kaggle.com/account)
2. Scroll to the "API" section
3. Click "Create New Token"
4. This downloads `kaggle.json` with your credentials

### 2. Configure Credentials

**Option A: Environment Variables (Recommended)**

```bash
export KAGGLE_USERNAME=your_username
export KAGGLE_API_KEY=your_api_key
```

Or add to your `~/.zshrc` or `~/.bashrc`:

```bash
echo 'export KAGGLE_USERNAME=your_username' >> ~/.zshrc
echo 'export KAGGLE_API_KEY=your_api_key' >> ~/.zshrc
source ~/.zshrc
```

**Option B: Using .env File**

Create a `.env` file in your project directory:

```env
KAGGLE_USERNAME=your_username
KAGGLE_API_KEY=your_api_key
```

## Usage

### With Claude Desktop

The recommended way to use Kaggle MCP is with Claude Desktop.

1. **Locate your Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add the Kaggle MCP server configuration:**

```json
{
  "mcpServers": {
    "kaggle": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/kaggle-mcp",
        "run",
        "kaggle_mcp/server.py"
      ],
      "env":{
          "KAGGLE_USERNAME": "YOUR_KAGGLE_USERNAME",
          "KAGGLE_API_KEY": "YOUR_KAGGLE_API_KEY"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Start using Kaggle through Claude!**

Try asking Claude:
- "List the latest Kaggle competitions"
- "Download the Titanic dataset"
- "Show me my recent competition submissions"
- "Search for NLP datasets"

### Standalone Usage

Run the MCP server directly:

```bash
kaggle-mcp
```

Or as a Python module:

```bash
python -m kaggle_mcp
```


## Available Tools

### Competitions (8 tools)

| Tool | Description |
|------|-------------|
| `competitions_list` | List and search available competitions |
| `competition_list_files` | List all files in a competition |
| `competition_download_file` | Download a specific competition file |
| `competition_download_files` | Download all competition files |
| `competition_submit` | Submit predictions to a competition |
| `competition_submissions` | View your submission history |
| `competition_leaderboard_view` | View the competition leaderboard |
| `competition_leaderboard_download` | Download leaderboard data |

### Datasets (10 tools)

| Tool | Description |
|------|-------------|
| `datasets_list` | Search and filter datasets |
| `dataset_metadata` | Get dataset metadata |
| `dataset_list_files` | List files in a dataset |
| `dataset_status` | Check dataset processing status |
| `dataset_download_file` | Download a specific dataset file |
| `dataset_download_files` | Download all dataset files |
| `dataset_create` | Create a new dataset |
| `dataset_initialize` | Initialize dataset metadata |
| `dataset_create_version` | Create a new dataset version |

### Kernels (7 tools)

| Tool | Description |
|------|-------------|
| `kernels_list` | Search and filter kernels |
| `kernel_list_files` | List files in a kernel |
| `kernel_initialize` | Initialize kernel metadata |
| `kernel_push` | Push a kernel to Kaggle |
| `kernel_pull` | Download a kernel |
| `kernel_output` | Download kernel output files |
| `kernel_status` | Check kernel execution status |

### Models (14 tools)

| Tool | Description |
|------|-------------|
| `models_list` | Search and filter models |
| `model_get` | Get model details and metadata |
| `model_initialize` | Initialize model metadata |
| `model_create` | Create a new model |
| `model_update` | Update model information |
| `model_delete` | Delete a model |
| `model_instance_get` | Get model instance details |
| `model_instance_initialize` | Initialize model instance metadata |
| `model_instance_create` | Create a new model instance |
| `model_instance_update` | Update a model instance |
| `model_instance_delete` | Delete a model instance |
| `model_instance_version_create` | Create a new model version |
| `model_instance_version_download` | Download a model version |
| `model_instance_version_delete` | Delete a model version |

## Examples

### Example 1: Working with Competitions

Ask Claude:
```
"List active Kaggle competitions about computer vision"
```

Claude will use the `competitions_list` tool to search and display relevant competitions.

### Example 2: Downloading Datasets

Ask Claude:
```
"Download the Titanic dataset to my Downloads folder"
```

Claude will use `dataset_download_files` to fetch all dataset files.

### Example 3: Submitting to Competitions

Ask Claude:
```
"Submit my predictions.csv to the Titanic competition with the message 'Initial baseline model'"
```

Claude will use `competition_submit` to upload your submission.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
