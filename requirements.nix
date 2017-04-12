# generated using pypi2nix tool (version: 1.8.0)
# See more at: https://github.com/garbas/pypi2nix
#
# COMMAND:
#   pypi2nix -V 2.7 -r /var/folders/r5/p283946j68v_9k03dcmhy3rm0000gn/T/pypi2nix/05b9a99bf6e1284d916712e53959bde4/buildout_requirements.txt --verbose
#

{ pkgs ? import <nixpkgs> {}
}:

let

  inherit (pkgs) makeWrapper;
  inherit (pkgs.stdenv.lib) fix' extends inNixShell;

  pythonPackages =
  import "${toString pkgs.path}/pkgs/top-level/python-packages.nix" {
    inherit pkgs;
    inherit (pkgs) stdenv;
    python = pkgs.python27Full;
  };

  commonBuildInputs = [];
  commonDoCheck = false;

  withPackages = pkgs':
    let
      pkgs = builtins.removeAttrs pkgs' ["__unfix__"];
      interpreter = pythonPackages.buildPythonPackage {
        name = "python27Full-interpreter";
        buildInputs = [ makeWrapper ] ++ (builtins.attrValues pkgs);
        buildCommand = ''
          mkdir -p $out/bin
          ln -s ${pythonPackages.python.interpreter}               $out/bin/${pythonPackages.python.executable}
          for dep in ${builtins.concatStringsSep " "               (builtins.attrValues pkgs)}; do
            if [ -d "$dep/bin" ]; then
              for prog in "$dep/bin/"*; do
                if [ -f $prog ]; then
                  ln -s $prog $out/bin/`basename $prog`
                fi
              done
            fi
          done
          for prog in "$out/bin/"*; do
            wrapProgram "$prog" --prefix PYTHONPATH : "$PYTHONPATH"
          done
          pushd $out/bin
          ln -s ${pythonPackages.python.executable} python
          popd
        '';
        passthru.interpreter = pythonPackages.python;
      };
    in {
      __old = pythonPackages;
      inherit interpreter;
      mkDerivation = pythonPackages.buildPythonPackage;
      packages = pkgs;
      overrideDerivation = drv: f:
        pythonPackages.buildPythonPackage (drv.drvAttrs // f drv.drvAttrs);
      withPackages = pkgs'':
        withPackages (pkgs // pkgs'');
    };

  python = withPackages {};

  generated = self: {

    "BeautifulSoup" = python.mkDerivation {
      name = "BeautifulSoup-3.2.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/1e/ee/295988deca1a5a7accd783d0dfe14524867e31abb05b6c0eeceee49c759d/BeautifulSoup-3.2.1.tar.gz"; sha256 = "6a8cb4401111e011b579c8c52a51cdab970041cc543814bbd9577a4529fe1cdb"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.psfl;
        description = "HTML/XML parser for quick-turnaround applications like screen-scraping.";
      };
    };



    "WSGIProxy2" = python.mkDerivation {
      name = "WSGIProxy2-0.4.2";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/a9/f9/c14d410957042eb2a8e78bf1f665f06360d643614ff3e1e74a9fafaae09f/WSGIProxy2-0.4.2.zip"; sha256 = "a4b236fac5d4a2b51d9b3ed34cbe0d01aae173dce0ab9877f225b1dcdb4a6e8e"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."WebOb"
      self."six"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "UNKNOWN";
      };
    };



    "WebOb" = python.mkDerivation {
      name = "WebOb-1.5.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/3c/63/3c3c183cf9ba0e30fe5d72d12c511af3bc5493b48e00f4f8ae3689a9d777/WebOb-1.5.1.tar.gz"; sha256 = "d8a9a153577f74b275dfd441ee2de4910eb2c1228d94186285684327e3877009"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."coverage"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "WSGI request and response object";
      };
    };



    "WebTest" = python.mkDerivation {
      name = "WebTest-2.0.20";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/4a/9d/db5a6d351404b15a1afbbf348d5f12d204bec57a8f871d6ee4bfe024ada7/WebTest-2.0.20.tar.gz"; sha256 = "bb137b96ce300eb4e43377804ed45be87674af7d414c4de46bba4d251bc4602f"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."WSGIProxy2"
      self."WebOb"
      self."beautifulsoup4"
      self."coverage"
      self."six"
      self."waitress"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "Helper to test WSGI applications";
      };
    };



    "apipkg" = python.mkDerivation {
      name = "apipkg-1.4";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/32/37/6ce6dbaa8035730efa95e60b09498ec17000d137742391ff46974d9ef859/apipkg-1.4.tar.gz"; sha256 = "2e38399dbe842891fe85392601aab8f40a8f4cc5a9053c326de35a1cc0297ac6"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "apipkg: namespace control and lazy-import mechanism";
      };
    };



    "beautifulsoup4" = python.mkDerivation {
      name = "beautifulsoup4-4.4.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/26/79/ef9a8bcbec5abc4c618a80737b44b56f1cb393b40238574078c5002b97ce/beautifulsoup4-4.4.1.tar.gz"; sha256 = "87d4013d0625d4789a4f56b8d79a04d5ce6db1152bb65f1d39744f7709a366b4"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "Screen-scraping library";
      };
    };



    "configparser" = python.mkDerivation {
      name = "configparser-3.5.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/7c/69/c2ce7e91c89dc073eb1aa74c0621c3eefbffe8216b3f9af9d3885265c01c/configparser-3.5.0.tar.gz"; sha256 = "5308b47021bc2340965c371f0f058cc6971a04502638d4244225c49d80db273a"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "This library brings the updated configparser from Python 3.5 to Python 2.6-3.5.";
      };
    };



    "coverage" = python.mkDerivation {
      name = "coverage-4.3.4";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/6e/33/01cb50da2d0582c077299651038371dba988248058e03c7a7c4be0c84c40/coverage-4.3.4.tar.gz"; sha256 = "eaaefe0f6aa33de5a65f48dd0040d7fe08cac9ac6c35a56d0a7db109c3e733df"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.asl20;
        description = "Code coverage measurement for Python";
      };
    };



    "decorator" = python.mkDerivation {
      name = "decorator-4.0.4";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/7a/ee/c8a9600cd5b5e09d08828371f9010926bf9cc67522be03d131529f7237a3/decorator-4.0.4.tar.gz"; sha256 = "5ad0c10fad31648cffa15ee0640eee04bbb1b843a02de26ad3700740768cc3e1"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.bsdOriginal;
        description = "Better living through Python with decorators";
      };
    };



    "enum34" = python.mkDerivation {
      name = "enum34-1.1.6";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/bf/3e/31d502c25302814a7c2f1d3959d2a3b3f78e509002ba91aea64993936876/enum34-1.1.6.tar.gz"; sha256 = "8ad8c4783bf61ded74527bffb48ed9b54166685e4230386a9ed9b1279e2df5b1"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.bsdOriginal;
        description = "Python 3.4 Enum backported to 3.3, 3.2, 3.1, 2.7, 2.6, 2.5, and 2.4";
      };
    };



    "execnet" = python.mkDerivation {
      name = "execnet-1.4.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/eb/ee/43729e7dee8772e69b3b01715ab9742790be2eace2d18cf53d219b9c31f8/execnet-1.4.1.tar.gz"; sha256 = "f66dd4a7519725a1b7e14ad9ae7d3df8e09b2da88062386e08e941cafc0ef3e6"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."apipkg"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "execnet: rapid multi-Python deployment";
      };
    };



    "flake8" = python.mkDerivation {
      name = "flake8-3.3.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/47/64/382631de5fd8dab367bedeff6b5b55fd9a7c883daa44f4032636e2d203ca/flake8-3.3.0.tar.gz"; sha256 = "b907a26dcf5580753d8f80f1be0ec1d5c45b719f7bac441120793d1a70b03f12"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."configparser"
      self."enum34"
      self."mccabe"
      self."pycodestyle"
      self."pyflakes"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "the modular source code checker: pep8, pyflakes and co";
      };
    };



    "gocept.cache" = python.mkDerivation {
      name = "gocept.cache-1.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/2f/ea/7e5b8923d39c3c3bfd082ebe00c34120b1a8d9b8aa84f3f002ffa4b1865c/gocept.cache-1.0.tar.gz"; sha256 = "f3874e59461826f37206d361e1b88f18c61c0090d55d70cfebc9c82d15680385"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."decorator"
      self."transaction"
      self."zope.testing"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.zpt21;
        description = "Cache descriptors for Python and Zope";
      };
    };



    "gocept.collmex" = python.mkDerivation {
      name = "gocept.collmex-1.7.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/f4/b4/e71ee94200ab7ec7f998dd9244ca852e7aaa0631f1282062d5f74afb21b8/gocept.collmex-1.7.0.zip"; sha256 = "4c01d511eee68e6f3fce98e46dac3d5de9216bae9c5ad85ed74aa0ce9ebc6eb1"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."WSGIProxy2"
      self."WebTest"
      self."gocept.cache"
      self."six"
      self."transaction"
      self."zope.deprecation"
      self."zope.interface"
      self."zope.testing"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.zpt21;
        description = "Python-bindings for the Collmex import/export API";
      };
    };



    "jira" = python.mkDerivation {
      name = "jira-0.16";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/d3/63/ac4d045934cf737f9f5c1ea9d85867613c43b910fd45e93c9e5ba5e568bc/jira-0.16.tar.gz"; sha256 = "3a30598a55ea2868cdf3466de78c7b8284a43655ee8af4755d3e837edc1b1e66"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."requests"
      self."requests-oauthlib"
      self."tlslite"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.bsdOriginal;
        description = "A library to ease use of the JIRA 5 REST APIs.";
      };
    };



    "mccabe" = python.mkDerivation {
      name = "mccabe-0.6.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/06/18/fa675aa501e11d6d6ca0ae73a101b2f3571a565e0f7d38e062eec18a91ee/mccabe-0.6.1.tar.gz"; sha256 = "dd8d182285a0fe56bace7f45b5e7d1a6ebcbf524e8f3bd87eb0f125271b8831f"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "McCabe checker, plugin for flake8";
      };
    };



    "oauthlib" = python.mkDerivation {
      name = "oauthlib-1.0.3";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/db/73/2a73deac557e3d2489e4aa14d606e20d6a445cd24a1f8661a6b1d26b41c6/oauthlib-1.0.3.tar.gz"; sha256 = "ef4bfe4663ca3b97a995860c0173b967ebd98033d02f38c9e1b2cbb6c191d9ad"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.bsdOriginal;
        description = "A generic, spec-compliant, thorough implementation of the OAuth request-signing logic";
      };
    };



    "py" = python.mkDerivation {
      name = "py-1.4.33";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/2a/a5/139ca93a9ffffd9fc1d3f14be375af3085f53cc490c508cf1c988b886baa/py-1.4.33.tar.gz"; sha256 = "1f9a981438f2acc20470b301a07a496375641f902320f70e31916fe3377385a9"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "library with cross-python path, ini-parsing, io, code, log facilities";
      };
    };



    "pyactiveresource" = python.mkDerivation {
      name = "pyactiveresource-1.0.2";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/95/e3/07e732b5004873c280803b52c26d7a413c6088dd3db16718fc1bac9629ca/pyactiveresource-1.0.2.tar.gz"; sha256 = "afec5bf05e2efa0f875cb259c8709b409710694a6dded28c8abedac44182932f"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "ActiveResource for Python";
      };
    };



    "pycodestyle" = python.mkDerivation {
      name = "pycodestyle-2.3.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/e1/88/0e2cbf412bd849ea6f1af1f97882add46a374f4ba1d2aea39353609150ad/pycodestyle-2.3.1.tar.gz"; sha256 = "682256a5b318149ca0d2a9185d365d8864a768a28db66a84a2ea946bcc426766"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "Python style guide checker";
      };
    };



    "pyflakes" = python.mkDerivation {
      name = "pyflakes-1.5.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/5b/b7/dcd6ebc826065ca4ccd2406aac4378e1df6eb91124625d45d520219932a1/pyflakes-1.5.0.tar.gz"; sha256 = "aa0d4dff45c0cc2214ba158d29280f8fa1129f3e87858ef825930845146337f4"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "passive checker of Python programs";
      };
    };



    "pync" = python.mkDerivation {
      name = "pync-1.6.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/01/69/04dbd2ddf85a24faf116821e89bb188e1c7c666e8803ba7a08dc7783ae11/pync-1.6.1.tar.gz"; sha256 = "85737aab9fc69cf59dc9fe831adbe94ac224944c05e297c98de3c2413f253530"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."python-dateutil"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "Python Wrapper for Mac OS 10.8 Notification Center";
      };
    };



    "pytest" = python.mkDerivation {
      name = "pytest-2.9.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/fb/da/7efd1506b067a45ddaf3e13f846f466538882071b9793273f06944e7e23b/pytest-2.9.0.tar.gz"; sha256 = "6fad53ccbf0903c69db93d67b83df520818b06c7597ed8a8407bc5fdffd5e40e"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."py"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "pytest: simple powerful testing with Python";
      };
    };



    "pytest-cache" = python.mkDerivation {
      name = "pytest-cache-1.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/d1/15/082fd0428aab33d2bafa014f3beb241830427ba803a8912a5aaeaf3a5663/pytest-cache-1.0.tar.gz"; sha256 = "be7468edd4d3d83f1e844959fd6e3fd28e77a481440a7118d430130ea31b07a9"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."execnet"
      self."pytest"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.gpl1;
        description = "pytest plugin with mechanisms for caching across test runs";
      };
    };



    "pytest-cov" = python.mkDerivation {
      name = "pytest-cov-2.2.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/39/07/bdd2d985ae7ac726cc5e7a6a343b585570bf1f9f7cb297a9cd58a60c7c89/pytest-cov-2.2.1.tar.gz"; sha256 = "a8b22e53e7f3b971454c35df99dffe21f4749f539491e935c55d3ff7e1b284fa"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."coverage"
      self."pytest"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.bsdOriginal;
        description = "Pytest plugin for measuring coverage.";
      };
    };



    "pytest-flake8" = python.mkDerivation {
      name = "pytest-flake8-0.2";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/f0/e6/fc5a510a67f3972f6ca121a60933ce22606002462d1d5489c72330491426/pytest-flake8-0.2.tar.gz"; sha256 = "58ab00be8d0361827f011cb2ba31ec3770f0797c18fcff48ed93d73fe058f418"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."flake8"
      self."pytest"
      self."pytest-cache"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.bsdOriginal;
        description = "pytest plugin to check FLAKE8 requirements";
      };
    };



    "pytest-rerunfailures" = python.mkDerivation {
      name = "pytest-rerunfailures-1.0.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/15/b1/346bffb2a25ef5aef4e191dc0b95d4eea01a38b8152109449583ccdceccc/pytest-rerunfailures-1.0.1.tar.gz"; sha256 = "afaf6928a3824dc6543c826c18af19f1bce497ef7596dfdbfaffe6558c16abe4"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."pytest"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mpl20;
        description = "pytest plugin to re-run tests to eliminate flaky failures";
      };
    };



    "pytest-sugar" = python.mkDerivation {
      name = "pytest-sugar-0.5.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/3f/f4/1cd72d9f81f71d985256cd1dab43431afa2a1670fc20217906c8149abb1c/pytest-sugar-0.5.1.tar.gz"; sha256 = "9c461a4cf5ef5bf9ce8c6c33706cfb88a78dcdab5604ad1c6d2902b9ed73fcf3"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."pytest"
      self."termcolor"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.bsdOriginal;
        description = "py.test is a plugin for py.test that changes the default look and feel of py.test (e.g. progressbar, show tests that fail instantly).";
      };
    };



    "python-dateutil" = python.mkDerivation {
      name = "python-dateutil-2.4.2";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/b6/ff/5eaa688dd8ce78913f47438f9b40071a560126ac3e95f9b9be27dfe546a7/python-dateutil-2.4.2.tar.gz"; sha256 = "3e95445c1db500a344079a47b171c45ef18f57d188dffdb0e4165c71bea8eb3d"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."six"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.bsdOriginal;
        description = "Extensions to the standard Python datetime module";
      };
    };



    "requests" = python.mkDerivation {
      name = "requests-2.8.1";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/38/2d/290d33417c079a5248fcd06b0b8492acdd1851e54e4bdad54c3859dab600/requests-2.8.1.tar.gz"; sha256 = "84fe8d5bf4dcdcc49002446c47a146d17ac10facf00d9086659064ac43b6c25b"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.asl20;
        description = "Python HTTP for Humans.";
      };
    };



    "requests-oauthlib" = python.mkDerivation {
      name = "requests-oauthlib-0.5.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/bd/30/7b69ccc1675052dbcb51b459fa94034e5ff2be1eccfcdfe3d88488f4c8aa/requests-oauthlib-0.5.0.tar.gz"; sha256 = "658d9aba85338be8c1d1532c9fb5807b381dc7166e469ff0f62fcaa4240d9eb8"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."oauthlib"
      self."requests"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.bsdOriginal;
        description = "OAuthlib authentication support for Requests.";
      };
    };



    "six" = python.mkDerivation {
      name = "six-1.10.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/b3/b2/238e2590826bfdd113244a40d9d3eb26918bd798fc187e2360a8367068db/six-1.10.0.tar.gz"; sha256 = "105f8d68616f8248e24bf0e9372ef04d3cc10104f1980f54d57b2ce73a5ad56a"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "Python 2 and 3 compatibility utilities";
      };
    };



    "termcolor" = python.mkDerivation {
      name = "termcolor-1.1.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/8a/48/a76be51647d0eb9f10e2a4511bf3ffb8cc1e6b14e9e4fab46173aa79f981/termcolor-1.1.0.tar.gz"; sha256 = "1d6d69ce66211143803fbc56652b41d73b4a400a2891d7bf7a1cdf4c02de613b"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.mit;
        description = "ANSII Color formatting for output in terminal.";
      };
    };



    "tlslite" = python.mkDerivation {
      name = "tlslite-0.4.9";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/92/2b/7904cf913d9bf150b3e408a92c9cb5ce0b97a9ec19f998af48bf4c607f0e/tlslite-0.4.9.tar.gz"; sha256 = "9b9a487694c239efea8cec4454a99a56ee1ae1a5f3af0858ccf8029e2ac2d42d"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = "public domain and BSD";
        description = "tlslite implements SSL and TLS.";
      };
    };



    "transaction" = python.mkDerivation {
      name = "transaction-1.4.4";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/87/53/b2b35be9aea0f4cb361c92e71fb6d0ced5ce896df24b7a56d75579caa8dc/transaction-1.4.4.tar.gz"; sha256 = "1781a0c74e3d2320a2a7fc048ff0d51b790d4f81062c8fcb12e3d29968646f34"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."coverage"
      self."zope.interface"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.zpt21;
        description = "Transaction management for Python";
      };
    };



    "waitress" = python.mkDerivation {
      name = "waitress-0.8.10";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/05/a1/56049f664a045fd7f789d0d291d3b2f97d6ad095b2ff2d6a07e0ad0c2a9b/waitress-0.8.10.tar.gz"; sha256 = "7c40c1af0f0c254edb25153621a1e825bc1af2f7bf41a74b4bb8ee6d544ef604"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."coverage"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.zpt21;
        description = "Waitress WSGI server";
      };
    };



    "zope.cachedescriptors" = python.mkDerivation {
      name = "zope.cachedescriptors-4.1.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/58/f3/a8f4657fd45dd0c6ca6cb1d55ca452cdacf33bebc34561df284bfe2001f4/zope.cachedescriptors-4.1.0.tar.gz"; sha256 = "a7dbc94528444acd8c15b04750f64ebfda07b321f1ececaf5a6b5353439c195d"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [ ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.zpt21;
        description = "Method and property caching decorators";
      };
    };



    "zope.deprecation" = python.mkDerivation {
      name = "zope.deprecation-4.1.2";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/c1/d3/3919492d5e57d8dd01b36f30b34fc8404a30577392b1eb817c303499ad20/zope.deprecation-4.1.2.tar.gz"; sha256 = "fed622b51ffc600c13cc5a5b6916b8514c115f34f7ea2730409f30c061eb0b78"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."coverage"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.zpt21;
        description = "Zope Deprecation Infrastructure";
      };
    };



    "zope.exceptions" = python.mkDerivation {
      name = "zope.exceptions-4.0.8";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/8f/b7/eba9eca6841fa47d9a30f71a602be7615bff4f8e11f85c2840b88a77c68a/zope.exceptions-4.0.8.tar.gz"; sha256 = "f43bcbb7e4f043565d4322db6ea50dd5a7b71cd03bb37f66791d6b6394529d7f"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."coverage"
      self."zope.interface"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.zpt21;
        description = "Zope Exceptions";
      };
    };



    "zope.interface" = python.mkDerivation {
      name = "zope.interface-4.1.3";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/9d/81/2509ca3c6f59080123c1a8a97125eb48414022618cec0e64eb1313727bfe/zope.interface-4.1.3.tar.gz"; sha256 = "2e221a9eec7ccc58889a278ea13dcfed5ef939d80b07819a9a8b3cb1c681484f"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."coverage"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.zpt21;
        description = "Interfaces for Python";
      };
    };



    "zope.testing" = python.mkDerivation {
      name = "zope.testing-4.5.0";
      src = pkgs.fetchurl { url = "https://pypi.python.org/packages/a3/07/164a6bf2b6979e136986548e70807fbe15d6eaf13a6ea455c357dd8f616d/zope.testing-4.5.0.tar.gz"; sha256 = "1a2418f715db09a39da7399fbfc2ff60c02bfad42fd9dd6c2d84c2fd61a76ffb"; };
      doCheck = commonDoCheck;
      buildInputs = commonBuildInputs;
      propagatedBuildInputs = [
      self."zope.exceptions"
      self."zope.interface"
    ];
      meta = with pkgs.stdenv.lib; {
        homepage = "";
        license = licenses.zpt21;
        description = "Zope testing helpers";
      };
    };

  };
  overrides = import ./requirements_override.nix { inherit pkgs python; };
  commonOverrides = [

  ];

in python.withPackages
   (fix' (pkgs.lib.fold
            extends
            generated
            ([overrides] ++ commonOverrides)
         )
   )