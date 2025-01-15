//
//  ExhibitsDetailView.swift
//  eyeson
//
//  Created by 조승용 on 8/5/24.
//

import SwiftUI
import Kingfisher

struct ExhibitsDetailView: View {
    @StateObject private var viewModel = ExhibitsDetailViewModel()
    @State private var isNavigatingToExhibitInfo = false
    @State private var searchText = ""
    @State private var hasLoadedData = false
    @State private var sortOrder: SortOrder = .title

    var exhibit: ExhibitList
    
    enum SortOrder {
           case title, artist
       }

    var body: some View {
        VStack {
            Picker("정렬 기준", selection: $sortOrder) {
                            Text("작품제목 순서").tag(SortOrder.title)
                            Text("작가명 순서").tag(SortOrder.artist)
                        }
                        .pickerStyle(SegmentedPickerStyle())
                        .padding(.horizontal)
            
            if viewModel.isLoading {
                ProgressView("로딩중")
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .foregroundColor(.red)
            } else {
                List {
                    Section(header: Text("나의 모든 순간")
                        .foregroundColor(.black)
                        .accessibilityLabel("전시제목: 나의 모든 순간")
                    ) {
                        ForEach(viewModel.exhibits.filter { exhibit in
                            searchText.isEmpty || exhibit.title.localizedCaseInsensitiveContains(searchText)
                        }
                        
                            .sorted {
                                                            switch sortOrder {
                                                            case .title:
                                                                return $0.title < $1.title
                                                            case .artist:
                                                                return $0.artist < $1.artist
                                                            }
                                                        }
                        ) { exhibit in
                            NavigationLink(destination: ArtworkView(eng_id: exhibit.id)) {
                                HStack {
                                    KFImage(URL(string: exhibit.imageUrl))
                                        .placeholder {
                                        ProgressView()
                                            .frame(width: 65, height: 55)
                                        }
                                        .resizable()
                                        .scaledToFit()
                                        .frame(width: 65, height: 55)
                                        .accessibilityLabel("작품 이미지")
                                        
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
            Spacer()
        }
        .onAppear {
            if !hasLoadedData {
                viewModel.fetchExhibits()
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
                    isNavigatingToExhibitInfo = true
                }) {
                    HStack(spacing: 2) {
                        Text("전시정보")
                    }
                }
            }
        }
    }
}
    
    struct CustomButtonsView: View {
        @Binding var isNavigatingToExhibitInfo: Bool
        
        var body: some View {
            Button(action: {
                isNavigatingToExhibitInfo = true
            }) {
                HStack(spacing: 2) {
                    Image(systemName: "info.circle")
                        .foregroundColor(Color.customGray1)
                    Text("전시정보")
                        .font(.system(size: 14))
                        .foregroundColor(Color.customGray1)
                }
            }
        }
    }



#Preview {
    ExhibitsDetailView(exhibit: ExhibitList(image: "image_museum", mainText: "Every Moment of Mine", subText1: "서울", subText2: "노들갤러리", subText3: "9.4-9.11"))
}

