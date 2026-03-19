# airis_app

## Build APK (Buildozer)

This project builds an Android APK using Buildozer.

### Prerequisites
- Python 3.10+
- Buildozer
- Java JDK 17+
- Android SDK/NDK dependencies required by Buildozer

### Build command
From the repository root, run:

```bash
buildozer android debug
```

The generated debug APK is typically written to:

```text
bin/airis-0.1-debug.apk
```

### GitHub Actions build
A CI workflow is available at `.github/workflows/android.yml` and can be triggered by:
- pushes to `main`
- pull requests
- manual `workflow_dispatch`

The built APK is uploaded as the `airis-apk` artifact.

### Notes
- App metadata and Android API/NDK settings are configured in `buildozer.spec`.
- If this is your first build, Buildozer may take significant time while downloading toolchains.
