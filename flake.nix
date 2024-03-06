{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
    flake-root.url = "github:srid/flake-root";
    mission-control.url = "github:Platonic-Systems/mission-control";
  };

  outputs = inputs @ {
    self,
    flake-parts,
    nixpkgs,
    ...
  }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      imports = [
        inputs.treefmt-nix.flakeModule
        inputs.flake-root.flakeModule
        inputs.mission-control.flakeModule
      ];
      systems = [
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
        "x86_64-linux"
      ];

      flake = {
      };

      perSystem = {
        self',
        inputs',
        system,
        lib,
        config,
        pkgs,
        ...
      }: {
        treefmt.config = {
          inherit (config.flake-root) projectRootFile;
          package = pkgs.treefmt;

          programs.alejandra.enable = true;
          programs.black.enable = true;
          programs.prettier.enable = true;
        };

        mission-control.scripts = {
          fmt = {
            description = "Format the source tree";
            exec = config.treefmt.build.wrapper;
            category = "Dev Tools";
          };
        };

        packages = {
        };

        devShells.default = pkgs.mkShell rec {
          name = "powerai";

          buildInputs = with pkgs; [
            (python311.withPackages (ps:
              with ps; [
                virtualenv
                pip
              ]))
            yarn
            nodejs_21

            zlib
            stdenv.cc.cc.lib
            libGL
            glib
          ];

          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath buildInputs;

          inputsFrom = [
            config.flake-root.devShell
            config.mission-control.devShell
          ];
        };
      };
    };
}
