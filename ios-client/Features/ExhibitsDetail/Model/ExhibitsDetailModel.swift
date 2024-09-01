//
//  ExhibitsDetailModel.swift
//  eyeson
//
//  Created by 조승용 on 8/6/24.
//

import Foundation
import SwiftUI

struct ExhibitDetailList: Identifiable {
    let id: String
    let explanation: String
    let description: String
    let comment: String
    let meta: ArtMetaData
}

struct ArtMetaData {
    let title: String
    let artist: String
    let style: String
    let emotion: String
}

let exhibitDetails: [ExhibitDetailList] = [
    ExhibitDetailList(
        id: "artwork_example",
        explanation: "작가는 자신이 좋아하는 게임 속 캐릭터들을 그리며 느끼는 기쁨과 즐거움을 표현. 캐릭터들이 마음껏 뛰어놀고 즐거워하는 모습을 담음.",
        description: "갈색 배경의 종이 위에 다양한 게임 캐릭터들이 그려져 있습니다. 캐릭터들은 서로 다른 포즈와 형태를 하고 있으며, 다양한 모습으로 그려져 있습니다.",
        comment: "이 작품은 게임을 좋아하는 작가가 자신이 좋아하는 게임 속 캐릭터들을 그리며 느끼는 기쁨과 즐거움을 표현한 것입니다. 게임 속 캐릭터들이 마음껏 뛰어놀고 즐거워하는 모습을 보여주고 있습니다.",
        meta: ArtMetaData(
            title: "Marathon of Contumelious1",
            artist: "홍준호",
            style: "스크래치 / 작화 연도 : 2024 / 가로 54 * 세로 39cm",
            emotion: "행복"
        )
    ),
    ExhibitDetailList(
        id: "artwork_example2",
        explanation: "작가는 자신이 좋아하는 게임 속 캐릭터들을 그리며 느끼는 기쁨과 즐거움을 표현. 캐릭터들이 마음껏 뛰어놀고 즐거워하는 모습을 담음.",
        description: "갈색 배경의 종이 위에 다양한 게임 캐릭터들이 그려져 있습니다. 캐릭터들은 서로 다른 포즈와 형태를 하고 있으며, 다양한 모습으로 그려져 있습니다.",
        comment: "이 작품은 게임을 좋아하는 작가가 자신이 좋아하는 게임 속 캐릭터들을 그리며 느끼는 기쁨과 즐거움을 표현한 것입니다. 게임 속 캐릭터들이 마음껏 뛰어놀고 즐거워하는 모습을 보여주고 있습니다.",
        meta: ArtMetaData(
            title: "abcd 모나리자",
            artist: "조승용",
            style: "스크래치 / 작화 연도 : 2024 / 가로 54 * 세로 39cm",
            emotion: "행복"
        )
    )
]
