# Migrating an existing GitHub repository to the clean layout

The release archive contains the **complete** Streamlit project, with `app.py` still at the root. The Streamlit Community Cloud entry point remains `app.py`.

## Recommended approach (local Git checkout)

1. Download and extract `Delivery_Exception_AI_GitHub_Clean_v2_4_0.zip` into a temporary directory.
2. Clone or open your existing public GitHub repository locally.
3. Copy the **contents** of the extracted archive into the repository root (not the enclosing directory).
4. Delete these *old root-level* files after verifying that their relocated copies exist:
   - `agent_flow.py`
   - `decision_package.py`
   - `oversight_status.py`
   - `replay_data.py`
   - `review_evidence.py`
   - `storyline.py`
   - `style.css`
   - `PUBLICATION_CHECKLIST.md`
5. Keep `app.py`, `README.md`, `requirements.txt` and `.gitignore` at the root. Keep `.streamlit/config.toml`, `src/`, `assets/`, `data/`, `docs/`, `scripts/`, `tests/` under their respective folders.
6. Review all public files for privacy and internal-policy content before committing.
7. From the repository folder, run:

   ```bash
   python -m pip install -r requirements.txt
   python -m pip install pytest
   python -m pytest -q
   streamlit run app.py
   ```

8. Commit the additions and deletions **together** so no deployed intermediate state breaks imports:

   ```bash
   git add -A
   git commit -m "Organize Streamlit demo repository and improve project README"
   git push
   ```

9. Confirm on GitHub that the home page shows only the four root files plus organised folders, and that the README renders the solution introduction, diagram, results and bottom-of-page version history.
10. Wait for Streamlit Community Cloud redeployment and confirm that the **v2.4.0** footer and Agent Flow still work.

> **Important:** Merely uploading the new files in GitHub's web interface will not remove the earlier root-level helpers. Delete the eight old root files explicitly (or use the Git workflow above) to avoid duplicate modules and a cluttered root. Do not delete a file before verifying its relocated copy exists.

## Data and behaviour guarantees

This is a **repository organisation** update, not a new model run or replay refresh. `data/recorded_cases.json`, `assets/shp006_story.mp4`, and the stylesheet are unchanged. `app.py` changes only import paths and the stylesheet path; the six workspaces, recorded decisions, metrics, stories, playback configuration and architecture content remain as in V2.4.0.
