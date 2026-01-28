package ca.tkacz.mycampusgo

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import ca.tkacz.mycampusgo.data.EventSummary
import ca.tkacz.mycampusgo.databinding.ItemEventBinding

class EventAdapter(
    private val onClick: (EventSummary) -> Unit
) : ListAdapter<EventSummary, EventAdapter.VH>(Diff) {

    object Diff : DiffUtil.ItemCallback<EventSummary>() {
        override fun areItemsTheSame(oldItem: EventSummary, newItem: EventSummary) =
            oldItem.slug == newItem.slug

        override fun areContentsTheSame(oldItem: EventSummary, newItem: EventSummary) =
            oldItem == newItem
    }

    inner class VH(private val binding: ItemEventBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(e: EventSummary) {
            binding.eventTitle.text = e.title
            binding.eventTime.text = e.start ?: ""
            binding.eventLocation.text = e.location ?: ""
            binding.eventExcerpt.text = e.excerpt ?: ""

            binding.root.setOnClickListener { onClick(e) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val binding = ItemEventBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return VH(binding)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.bind(getItem(position))
    }
}
