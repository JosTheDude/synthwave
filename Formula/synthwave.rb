class Synthwave < Formula
  include Language::Python::Virtualenv

  desc "Tiny, vibey terminal radio for Lofi Girl's live streams"
  homepage "https://github.com/JosTheDude/synthwave"
  url "https://github.com/JosTheDude/synthwave.git", revision: "02dcebd5e05c55e04d56cb9e92b027d8a1a55e05"
  version "0.1.0-02dcebd"
  license "MIT"
  head "https://github.com/JosTheDude/synthwave.git", branch: "main"

  depends_on "mpv"
  depends_on "python@3.13"
  depends_on "yt-dlp"

  def install
    venv = virtualenv_create(libexec, "python3.13")
    venv.pip_install_and_link buildpath
  end

  test do
    system libexec/"bin/python", "-c", "import synthwave.app, synthwave.stations"
  end
end
