import ProjectDescription

let project = Project(
    name: "eyeson",
    targets: [
        .target(
            name: "eyeson",
            destinations: .iOS,
            product: .app,
            bundleId: "io.tuist.eyeson",
            infoPlist: .extendingDefault(
                with: [
                    "UILaunchScreen": [
                        "UIColorName": "",
                        "UIImageName": "",
                    ],
                ]
            ),
            sources: ["eyeson/Sources/**"],
            resources: ["eyeson/Resources/**"],
            dependencies: []
        ),
        .target(
            name: "eyesonTests",
            destinations: .iOS,
            product: .unitTests,
            bundleId: "io.tuist.eyesonTests",
            infoPlist: .default,
            sources: ["eyeson/Tests/**"],
            resources: [],
            dependencies: [.target(name: "eyeson")]
        ),
    ]
)
