// Fixture: intentionally problematic Liquid Glass usage.
// Used to verify audit_liquid_glass.py surfaces the expected leads.
import SwiftUI

struct BadFeedView: View {
    @State private var items: [Item] = []
    @State private var showSheet = false

    var body: some View {
        List {
            ForEach(items) { item in
                // LEAD: glass in a repeating content-layer row
                ItemCard(item: item)
                    .glassEffect(in: .rect(cornerRadius: 12))
            }
        }
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                // LEAD: raw glassEffect on a Button, inside a toolbar
                Button("Save") { }
                    .glassEffect()
            }
        }
        // LEAD: custom bar background fighting the system
        .toolbarBackground(.blue, for: .navigationBar)
        .sheet(isPresented: $showSheet) {
            DetailView()
                // LEAD: presentationBackground override
                .presentationBackground(.regularMaterial)
        }
    }
}

struct BadControlCluster: View {
    @State private var expanded = false

    var body: some View {
        HStack {
            // LEAD: glassEffectID with no @Namespace and no animation
            Button { expanded.toggle() } label: {
                Image(systemName: "plus")
            }
            .buttonStyle(.glass)
            .glassEffectID("toggle", in: someNamespace)

            // LEAD: hard-coded foreground on glass
            Text("Recording")
                .foregroundColor(.white)
                .glassEffect()

            // LEAD: magic opacity next to glass
            Circle()
                .glassEffect()
                .opacity(0.65)
        }
    }
}

struct BadMediaControls: View {
    var body: some View {
        // LEAD: clear glass — needs a dimming layer verified
        PlaybackButtons()
            .glassEffect(.clear, in: .capsule)
            // LEAD: interactive on possibly non-interactive content
            .glassEffect(.regular.interactive(true))
    }
}

struct BadLegacy: View {
    var body: some View {
        VStack { }
            // LEAD: availability branch — dead code if target >= 26
            .background {
                if #available(iOS 26, *) {
                    Color.clear.glassEffect()
                } else {
                    Color.clear.background(.ultraThinMaterial)
                }
            }
    }
}
