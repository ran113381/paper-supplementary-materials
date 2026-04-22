# GitHub Upload Steps

## Folder to Upload

Upload this folder as the repository root:

`github_public_repro_package`

Do not upload the larger private rebuild workspace around it.

## Before Upload

Check these items once:

1. `DATA_AVAILABILITY.md` correctly states that licensed raw data are not included.
2. `output/` contains only frozen exhibit files meant for review.
3. `paper/attachments/` contains only the public dictionary attachments you want to share.
4. No private raw-data folders or firm-level processed workbooks were copied into this package.

## Option A: Use GitHub Web + Local Git

1. Create a new empty repository on GitHub.
2. Do not auto-generate a new `README`, `.gitignore`, or license if you want to keep this package exactly as-is.
3. In a terminal, move into the package folder.
4. Run:

```powershell
git init
git branch -M main
git add .
git commit -m "Initial public reproduction package"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## Option B: If You Already Have a Repository

1. Copy the contents of this package into the repository root.
2. Run:

```powershell
git add .
git commit -m "Update public reproduction package"
git push
```

## Recommended Repository Description

Suggested short description:

`Public manuscript-supporting reproduction package with frozen exhibits, dictionary materials, and documentation.`

## Important Wording

In the repository description and README, avoid claiming:

- full raw-data release
- one-click end-to-end rerun
- unrestricted public access to licensed source data

Use language such as:

`This repository provides manuscript-supporting frozen outputs and public documentation; licensed raw data are not redistributed.`
