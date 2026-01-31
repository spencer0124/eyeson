//
//  ExhibitsDetailView.swift
//  eyeson
//
//  Created by 조승용 on 8/5/24.
//

import SwiftUI
import Kingfisher
import BetterSafariView

struct ExhibitsDetailView: View {
    @StateObject private var viewModel = ExhibitsDetailViewModel()
    @State private var isNavigatingToExhibitInfo = false
    @State private var searchText = ""
    @State private var hasLoadedData = false
    @State private var sortOrder: SortOrder = .artworknum
    
    @State var showSafari: Bool = false
    
    var exhibit: ExhibitList
    
    enum SortOrder {
           case title, artworknum
       }

    var body: some View {
        VStack {
            Picker("정렬 기준", selection: $sortOrder) {
                            Text("관람 순서").tag(SortOrder.artworknum)
                            Text("작품 제목 순서").tag(SortOrder.title)
                        }
                        .pickerStyle(SegmentedPickerStyle())
                        .padding(.horizontal)
            
            if viewModel.isLoading {
                ProgressView("로딩중")
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .foregroundColor(.red)
            } else {
                ExhibitsListView(exhibit: exhibit, searchText: $searchText, sortOrder: $sortOrder, paramUniqueId: exhibit.ParamUniqueId, viewModel: viewModel) // List 부분을 Subview로 분리
            }
            Spacer()
        }
        .fullScreenCover(isPresented: $showSafari) {
            if let url = URL(string: exhibit.ParamInfoUrl) {
                SafariView(
                    url: url,
                    configuration: SafariView.Configuration(
                        entersReaderIfAvailable: false,
                        barCollapsingEnabled: true
                    )
                )
            }
        }
        
        .onAppear {
            if !hasLoadedData {
                viewModel.fetchExhibits(uniqueId: exhibit.ParamUniqueId)
                hasLoadedData = true
            }
        }
        .background(
            NavigationLink(
                destination: ExhibitInfoView(),
                isActive: $isNavigatingToExhibitInfo,
                label: { EmptyView() }
            )
        )
        .navigationTitle("작품 목록")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: {
//                    isNavigatingToExhibitInfo = true
                    showSafari = true // 전시정보 보여줄 웹뷰 켜기
                    
                }) {
                    HStack(spacing: 2) {
                        Text("전시정보")
                    }
                    
                }
            }
        }
    }
    
    struct ExhibitsListView: View {
        let exhibit: ExhibitList
        @Binding var searchText: String
        @Binding var sortOrder: ExhibitsDetailView.SortOrder
        var paramUniqueId: String
        @ObservedObject var viewModel: ExhibitsDetailViewModel

        var body: some View {
            List {
                Section(header: Text(exhibit.ParamExhibitName)
                    .foregroundColor(.black)
                    .accessibilityLabel("전시제목: \(exhibit.ParamExhibitName)")
                ) {
                    ForEach(viewModel.exhibits.filter { exhibit in
                        searchText.isEmpty || exhibit.title.localizedCaseInsensitiveContains(searchText)
                    }
                    .sorted {
                        switch sortOrder {
                        case .title:
                            return $0.title < $1.title
                        case .artworknum:
                            return $0.artworknum < $1.artworknum
                        }
                    }
                    ) { exhibit in
                        NavigationLink(destination: ArtworkView(eng_id: exhibit.id, paramUniqueId: paramUniqueId)) {
                            HStack {
                                KFImage(URL(string: exhibit.imageUrl))
                                    .placeholder {
                                        ProgressView()
                                            .frame(width: 65, height: 55)
                                    }
                                    .resizable()
                                    .scaledToFit()
                                    .frame(width: 65, height: 55)
                                    .accessibilityLabel("\(exhibit.title) 작품 이미지")

                                Spacer()
                                    .frame(width: 20)
                                VStack(alignment: .leading) {
                                    Text(exhibit.title)
                                        .font(.headline)
                                        .accessibilityLabel("작품제목: \(exhibit.title)")
                                    Text(exhibit.artist)
                                        .font(.subheadline)
                                        .foregroundColor(.black)
                                        .accessibilityLabel("작가: \(exhibit.artist)")
                                }
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
            }
            .listStyle(PlainListStyle())
            .searchable(text: $searchText, placement: .automatic, prompt: "작품 검색하기")
        }
    }

    // ... (기존 코드) ...

}
    
    



#Preview {
    ExhibitsDetailView(exhibit: ExhibitList(image: "image_museum", mainText: "Every Moment of Mine", subText1: "서울", subText2: "노들갤러리", subText3: "9.4-9.11", endDate: Calendar.current.date(byAdding: .day, value: 7, to: Date())!, ParamUniqueId: "240904_everymoment", ParamExhibitName: "Every Moment of Mine", ParamInfoUrl: "https://www.startuptoday.kr/news/articleView.html?idxno=43596"))
}

